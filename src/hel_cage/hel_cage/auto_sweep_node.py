#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np
import csv
import os
import time
from datetime import datetime

class AutoSweepNode(Node):
    def __init__(self):
        super().__init__('auto_sweep_node')

        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        self.calib_dir = os.path.join(self.ws_root, 'calibration_files')
        os.makedirs(self.calib_dir, exist_ok=True)
        
        # ===== SPLIT SEQUENCE CONFIGURATION =====
        self.pwm_step = 10.0
        
        # Positive sequence: [0.0, 10.0 ... 250.0, 255.0]
        self.pwm_pos = list(np.arange(0.0, 255.0 + self.pwm_step, self.pwm_step))
        if self.pwm_pos[-1] > 255.0: 
            self.pwm_pos[-1] = 255.0
            
        # Negative sequence: [-10.0, -20.0 ... -250.0, -255.0]
        self.pwm_neg = list(np.arange(-self.pwm_step, -255.0 - self.pwm_step, -self.pwm_step))
        if self.pwm_neg[-1] < -255.0: 
            self.pwm_neg[-1] = -255.0
            
        # --- THE HARDWARE BODYGUARD ---
        self.actual_pwm = 0.0        
        self.max_pwm_slew_rate = 80.0 
        self.timer_period = 0.05     
        self.slew_per_tick = self.max_pwm_slew_rate * self.timer_period

        # ===== THE INDEPENDENT WATCHDOG =====
        self.last_tel_time = time.time()
        self.TIMEOUT_LIMIT = 1.0
        self.watchdog_tripped = False

        # Data arrays, Corrected for strict memory alignment
        combined_keys = self.pwm_neg + self.pwm_pos
        self.all_keys = sorted([float(k) for k in combined_keys])
        self.master_data = {}
        self.current_save_path = "" # Track the active file
        
        # Ambient Baseline Memory
        self.ambient_buffer = {'X': [], 'Y': [], 'Z': []}
        self.ambient_baseline = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}

        # Execution Pointers
        self.state = 'IDLE'
        self.auto_apply = False
        self.axes = ['X', 'Y', 'Z']
        self.current_axis_idx = 0
        self.current_pwm_idx = 0
        self.current_phase = 'POS' 
        self.post_spool_action = 'NONE'
        self.telemetry_buffer = []

        self.ctrl_sub = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        self.tel_sub = self.create_subscription(Vector3, 'telemetry', self.tel_cb, 10)
        self.pwm_pub = self.create_publisher(Vector3, 'pwm_cmd', 10)
        self.ctrl_pub = self.create_publisher(String, 'control_cmd', 10)

        self.timer = self.create_timer(self.timer_period, self.sweep_loop)
        self.get_logger().info("Relative Auto-Sweep Node Ready. Sensor Watchdog ACTIVE. Resolution: 1 PWM.")

    def ctrl_cb(self, msg):
        cmd = msg.data.strip()
        if cmd == "SWEEP:APPLY":
            self.start_sweep(apply=True)
        elif cmd == "SWEEP:SAVE_ONLY":
            self.start_sweep(apply=False)
        elif cmd == "ABORT":
            self.get_logger().warn("Network ABORT received. Engaging safe spool down.")
            self.post_spool_action = 'ABORT'
            self.state = 'SPOOL_TO_ZERO'

    def start_sweep(self, apply):
        if self.state != 'IDLE': return
        
        # Do not allow sweep to start if sensor is already dead
        if time.time() - self.last_tel_time > self.TIMEOUT_LIMIT:
            self.get_logger().error("START REJECTED. Sensor connection is absent.")
            return

        self.get_logger().info("--- STARTING 3-AXIS RELATIVE SWEEP ---")
        self.auto_apply = apply
        self.master_data = {k: [0.0, 0.0, 0.0] for k in self.all_keys}
        
        # Immediate File Generation
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_save_path = os.path.join(self.calib_dir, f"master_calib_relative_{ts}.csv")
        self.dump_to_disk()
        
        self.current_axis_idx = 0
        self.current_pwm_idx = 0
        self.current_phase = 'POS'
        self.actual_pwm = 0.0
        
        # Initiate baseline extraction protocol
        self.state = 'AMBIENT_SETTLE'

    def tel_cb(self, msg):
        # Update heartbeat and reset latch if sensor returns
        self.last_tel_time = time.time()
        if self.watchdog_tripped:
            self.get_logger().info("SENSOR SIGNAL RESTORED.")
            self.watchdog_tripped = False

        if self.state == 'AMBIENT_MEASURE':
            self.ambient_buffer['X'].append(msg.x)
            self.ambient_buffer['Y'].append(msg.y)
            self.ambient_buffer['Z'].append(msg.z)
        elif self.state == 'MEASURE':
            axis_name = self.axes[self.current_axis_idx]
            val = getattr(msg, axis_name.lower())
            self.telemetry_buffer.append(val)

    def sweep_loop(self):
        if self.state == 'IDLE': return

        if self.state == 'SAVE':
            self.get_logger().info(f"Sweep finalization complete. Final file at {self.current_save_path}")
            if self.auto_apply:
                self.ctrl_pub.publish(String(data=f"CALIB:{self.current_save_path}"))
            self.state = 'IDLE'
            return

        now = time.time()
        
        # === WATCHDOG TRIGGER ===
        if now - self.last_tel_time > self.TIMEOUT_LIMIT:
            if not self.watchdog_tripped:
                self.get_logger().error("SENSOR SIGNAL LOST. Intercepting Sweep. Engaging safe spool down. Data preserved.")
                self.watchdog_tripped = True
                
                # Hijack the state machine to execute physical descent
                self.post_spool_action = 'ABORT'
                self.state = 'SPOOL_TO_ZERO'
        
        # 1. DETERMINE TARGET PWM
        if self.state in ['SPOOL_TO_ZERO', 'AMBIENT_SETTLE', 'AMBIENT_MEASURE']:
            target_pwm = 0.0
        elif self.current_phase == 'POS':
            target_pwm = float(self.pwm_pos[self.current_pwm_idx])
        else:
            target_pwm = float(self.pwm_neg[self.current_pwm_idx])

        # 2. SLEW LOGIC
        diff = target_pwm - self.actual_pwm
        step = np.clip(diff, -self.slew_per_tick, self.slew_per_tick)
        self.actual_pwm += step

        # 3. PUBLISH
        axis = self.axes[self.current_axis_idx]
        cmd = Vector3()
        # Always output to all axes to guarantee zeroing
        cmd.x = self.actual_pwm if axis == 'X' else 0.0
        cmd.y = self.actual_pwm if axis == 'Y' else 0.0
        cmd.z = self.actual_pwm if axis == 'Z' else 0.0
        self.pwm_pub.publish(cmd)

        # 4. STATE TRANSITIONS
        if self.state == 'AMBIENT_SETTLE':
            if abs(self.actual_pwm) < 0.1:
                self.ambient_buffer = {'X': [], 'Y': [], 'Z': []}
                self.state_start_t = now
                self.state = 'AMBIENT_MEASURE'
                self.get_logger().info("Measuring ambient baseline. Standby 3 seconds.")

        elif self.state == 'AMBIENT_MEASURE':
            if now - self.state_start_t > 3.0:
                for ax in ['X', 'Y', 'Z']:
                    self.ambient_baseline[ax] = np.mean(self.ambient_buffer[ax]) if self.ambient_buffer[ax] else 0.0
                self.get_logger().info(f"Baseline -> X: {self.ambient_baseline['X']:.2f}, Y: {self.ambient_baseline['Y']:.2f}, Z: {self.ambient_baseline['Z']:.2f}")
                self.state = 'SLEW_TO_STEP'

        elif self.state == 'SLEW_TO_STEP':
            if abs(target_pwm - self.actual_pwm) < 0.1:
                self.state_start_t = now
                self.state = 'SETTLE'

        elif self.state == 'SETTLE':
            if now - self.state_start_t > 2.0: #change for time peroid
                self.telemetry_buffer = []
                self.state_start_t = now
                self.state = 'MEASURE'

        elif self.state == 'MEASURE':
            if now - self.state_start_t > 2.0: #change for time period
                raw_mean = np.mean(self.telemetry_buffer) if self.telemetry_buffer else 0.0
                # Apply the ambient correction subtraction
                relative_b = round(raw_mean - self.ambient_baseline[axis], 2)
                pwm_val = target_pwm
                
                self.master_data[pwm_val][self.current_axis_idx] = relative_b
                self.get_logger().info(f"{axis}-Axis | {pwm_val} PWM -> {relative_b} µT")
                
                # EXECUTE CONTINUOUS LIVE WRITE
                self.dump_to_disk()
                
                self.current_pwm_idx += 1
                
                # Check for array exhaustion
                active_array = self.pwm_pos if self.current_phase == 'POS' else self.pwm_neg
                if self.current_pwm_idx >= len(active_array):
                    if self.current_phase == 'POS':
                        self.get_logger().info(f"{axis}-Axis POS sweep complete. Spooling to 0...")
                        self.post_spool_action = 'START_NEG'
                        self.state = 'SPOOL_TO_ZERO'
                    else:
                        self.get_logger().info(f"{axis}-Axis NEG sweep complete. Spooling to 0...")
                        self.post_spool_action = 'NEXT_AXIS'
                        self.state = 'SPOOL_TO_ZERO'
                else:
                    self.state = 'SLEW_TO_STEP'

        elif self.state == 'SPOOL_TO_ZERO':
            if abs(self.actual_pwm) < 0.1:
                if self.post_spool_action == 'ABORT':
                    self.state = 'IDLE'
                    self.get_logger().warn("Hardware secured. Abort complete.")
                elif self.post_spool_action == 'START_NEG':
                    self.current_phase = 'NEG'
                    self.current_pwm_idx = 0
                    self.state = 'SLEW_TO_STEP'
                elif self.post_spool_action == 'NEXT_AXIS':
                    self.current_axis_idx += 1
                    if self.current_axis_idx >= len(self.axes):
                        self.state = 'SAVE'
                    else:
                        self.current_phase = 'POS'
                        self.current_pwm_idx = 0
                        self.get_logger().info(f"Switching to {self.axes[self.current_axis_idx]}-Axis.")
                        self.state = 'SLEW_TO_STEP'
                        
    def dump_to_disk(self):
        """Silently overwrites the active CSV with the latest matrix state."""
        if not self.current_save_path: return
        try:
            with open(self.current_save_path, 'w', newline='') as f:
                writer = csv.writer(f)
                for pwm in self.all_keys:
                    writer.writerow([pwm] + self.master_data[pwm])
        except Exception as e:
            self.get_logger().error(f"Live disk write failed: {e}")

def main():
    rclpy.init()
    node = AutoSweepNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().warn("CTRL+C DETECTED. Executing synchronous safe spool down.")
        
        while abs(node.actual_pwm) > 0.1:
            diff = 0.0 - node.actual_pwm
            step = np.clip(diff, -node.slew_per_tick, node.slew_per_tick)
            node.actual_pwm += step
            
            axis = node.axes[node.current_axis_idx]
            cmd = Vector3()
            cmd.x = node.actual_pwm if axis == 'X' else 0.0
            cmd.y = node.actual_pwm if axis == 'Y' else 0.0
            cmd.z = node.actual_pwm if axis == 'Z' else 0.0
            node.pwm_pub.publish(cmd)
            
            time.sleep(node.timer_period)
            
        node.get_logger().info("Hardware secured. Executing final disk flush.")
        node.dump_to_disk()
        node.state = 'IDLE'
        
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()