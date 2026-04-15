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

        # ===== WORKSPACE RESOLUTION =====
        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        self.calib_dir = os.path.join(self.ws_root, 'calibration_files')
        os.makedirs(self.calib_dir, exist_ok=True)
        
        # ===== SWEEP CONFIGURATION =====
        self.pwm_step = 10.0
        self.pwm_max = 255.0
        self.pwm_steps = list(np.arange(0, 260, self.pwm_step))
        if self.pwm_steps[-1] < self.pwm_max:
            self.pwm_steps.append(self.pwm_max)
            
        # --- THE HARDWARE BODYGUARD ---
        self.actual_pwm = 0.0        
        self.max_pwm_slew_rate = 80.0 # PROTECTS THE CYTRON DRIVERS
        self.timer_period = 0.05     
        self.slew_per_tick = self.max_pwm_slew_rate * self.timer_period

        self.master_data = {} 
        
        # Updated States: 'IDLE', 'RAMP_UP', 'SETTLE', 'MEASURE', 'RAMP_DOWN_AXIS', 'SAVE'
        self.state = 'IDLE'
        self.auto_apply = False
        
        self.axes = ['X', 'Y', 'Z']
        self.current_axis_idx = 0
        self.current_pwm_idx = 0
        self.telemetry_buffer = []

        # ===== ROS INTERFACES =====
        self.ctrl_sub = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        self.tel_sub = self.create_subscription(Vector3, 'telemetry', self.tel_cb, 10)
        self.pwm_pub = self.create_publisher(Vector3, 'pwm_cmd', 10)
        self.ctrl_pub = self.create_publisher(String, 'control_cmd', 10)

        self.timer = self.create_timer(self.timer_period, self.sweep_loop)
        self.get_logger().info("Axis-Safe Auto-Sweep Node Ready.")

    def ctrl_cb(self, msg):
        cmd = msg.data.strip()
        if cmd == "SWEEP:APPLY":
            self.start_sweep(apply=True)
        elif cmd == "SWEEP:SAVE_ONLY":
            self.start_sweep(apply=False)

    def start_sweep(self, apply):
        if self.state != 'IDLE': return
        self.get_logger().info("--- STARTING 3-AXIS MASTER SWEEP ---")
        self.auto_apply = apply
        self.master_data = {float(pwm): [0.0, 0.0, 0.0] for pwm in self.pwm_steps}
        self.current_axis_idx = 0
        self.current_pwm_idx = 0
        self.actual_pwm = 0.0
        self.state = 'RAMP_UP'

    def tel_cb(self, msg):
        if self.state == 'MEASURE':
            axis_name = self.axes[self.current_axis_idx].lower()
            val = getattr(msg, axis_name)
            self.telemetry_buffer.append(abs(val))

    def sweep_loop(self):
        # 1. Guard against IDLE
        if self.state == 'IDLE': return

        # 2. Handle SAVE state immediately (The Fix for the crash)
        if self.state == 'SAVE':
            self.save_to_csv()
            self.state = 'IDLE'
            return

        now = time.time()
        
        # 3. Determine TARGET PWM
        if self.state == 'RAMP_DOWN_AXIS':
            target_pwm = 0.0
        else:
            target_pwm = float(self.pwm_steps[self.current_pwm_idx])

        # 4. SLEW LOGIC
        diff = target_pwm - self.actual_pwm
        step = np.clip(diff, -self.slew_per_tick, self.slew_per_tick)
        self.actual_pwm += step

        # 5. PUBLISH to current axis (Now safe from IndexError)
        axis = self.axes[self.current_axis_idx]
        cmd = Vector3()
        setattr(cmd, axis.lower(), self.actual_pwm)
        self.pwm_pub.publish(cmd)

        # 6. STATE TRANSITIONS
        if self.state == 'RAMP_UP':
            if abs(target_pwm - self.actual_pwm) < 0.1:
                self.state_start_t = now
                self.state = 'SETTLE'

        elif self.state == 'SETTLE':
            if now - self.state_start_t > 0.5:
                self.telemetry_buffer = []
                self.state_start_t = now
                self.state = 'MEASURE'

        elif self.state == 'MEASURE':
            if now - self.state_start_t > 0.5:
                avg_b = round(np.mean(self.telemetry_buffer)) if self.telemetry_buffer else 0.0
                pwm_val = float(self.pwm_steps[self.current_pwm_idx])
                self.master_data[pwm_val][self.current_axis_idx] = avg_b
                self.get_logger().info(f"{self.axes[self.current_axis_idx]}-Axis | {pwm_val} PWM -> {avg_b:.2f} µT")
                self.current_pwm_idx += 1
                if self.current_pwm_idx >= len(self.pwm_steps):
                    self.get_logger().info(f"{axis}-Axis finished. Spooling down...")
                    self.state = 'RAMP_DOWN_AXIS'
                else:
                    self.state = 'RAMP_UP'

        elif self.state == 'RAMP_DOWN_AXIS':
            # Wait until current axis is at 0
            if abs(self.actual_pwm) < 0.1:
                # CHECK: Are there more axes left?
                if self.current_axis_idx >= len(self.axes) - 1:
                    # No more axes. Go to SAVE state.
                    self.state = 'SAVE'
                else:
                    # Reset PWM index and move to next axis
                    self.current_pwm_idx = 0
                    self.current_axis_idx += 1
                    self.get_logger().info(f"Switching to {self.axes[self.current_axis_idx]}-Axis.")
                    self.state = 'RAMP_UP'

    def save_to_csv(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"master_calib_{ts}.csv"
        save_path = os.path.join(self.calib_dir, filename)
        try:
            with open(save_path, 'w', newline='') as f:
                writer = csv.writer(f)
                for pwm in self.pwm_steps:
                    writer.writerow([float(pwm)] + self.master_data[float(pwm)])
            self.get_logger().info(f"SUCCESS: Calibration saved to {save_path}")
            if self.auto_apply:
                self.ctrl_pub.publish(String(data=f"CALIB:{save_path}"))
        except Exception as e:
            self.get_logger().error(f"Save failed: {e}")

def main():
    rclpy.init()
    rclpy.spin(AutoSweepNode())

if __name__ == '__main__':
    main()