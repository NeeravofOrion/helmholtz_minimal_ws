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
        # Build list of PWM targets: [0.0, 10.0, 20.0 ... 250.0, 255.0]
        self.pwm_steps = list(np.arange(0, 260, self.pwm_step))
        if self.pwm_steps[-1] < self.pwm_max:
            self.pwm_steps.append(self.pwm_max)
            
        self.master_data = {} 
        
        # State Machine: 'IDLE', 'DRIVE', 'SETTLE', 'MEASURE', 'SAVE'
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

        self.timer = self.create_timer(0.05, self.sweep_loop)
        self.get_logger().info("Fixed 3-Axis Auto-Sweep Node Ready.")

    def ctrl_cb(self, msg):
        cmd = msg.data.strip()
        # MATCHES YOUR GUI EXACTLY
        if cmd == "SWEEP:APPLY":
            self.start_sweep(apply=True)
        elif cmd == "SWEEP:SAVE_ONLY":
            self.start_sweep(apply=False)

    def start_sweep(self, apply):
        if self.state != 'IDLE': return
        self.get_logger().info("--- STARTING 3-AXIS MASTER SWEEP ---")
        self.auto_apply = apply
        
        # Reset data for a fresh run: { pwm_val: [Bx, By, Bz] }
        self.master_data = {float(pwm): [0.0, 0.0, 0.0] for pwm in self.pwm_steps}
        
        self.current_axis_idx = 0
        self.current_pwm_idx = 0
        self.state = 'DRIVE'

    def tel_cb(self, msg):
        if self.state == 'MEASURE':
            axis_name = self.axes[self.current_axis_idx].lower()
            # Capture the absolute value of the currently active axis
            val = getattr(msg, axis_name)
            self.telemetry_buffer.append(abs(val))

    def sweep_loop(self):
        if self.state == 'IDLE': return

        now = time.time()

        if self.state == 'DRIVE':
            pwm_val = float(self.pwm_steps[self.current_pwm_idx])
            axis = self.axes[self.current_axis_idx]
            
            # Energize ONLY the current axis
            cmd = Vector3()
            setattr(cmd, axis.lower(), pwm_val)
            self.pwm_pub.publish(cmd)
            
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
                
                # Save to master dictionary (X=0, Y=1, Z=2)
                self.master_data[pwm_val][self.current_axis_idx] = avg_b
                self.get_logger().info(f"{self.axes[self.current_axis_idx]}-Axis | {pwm_val} PWM -> {avg_b:.2f} µT")

                # Advance to next PWM step
                self.current_pwm_idx += 1
                if self.current_pwm_idx >= len(self.pwm_steps):
                    # Finished this axis, move to the next one
                    self.current_pwm_idx = 0
                    self.current_axis_idx += 1
                    
                    if self.current_axis_idx >= len(self.axes):
                        self.state = 'SAVE'
                    else:
                        self.state = 'DRIVE'
                else:
                    self.state = 'DRIVE'

        elif self.state == 'SAVE':
            self.pwm_pub.publish(Vector3()) # Power down
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"master_calib_{ts}.csv"
            save_path = os.path.join(self.calib_dir, filename)
            
            try:
                with open(save_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    for pwm in self.pwm_steps:
                        # Writes: PWM, Bx, By, Bz
                        writer.writerow([float(pwm)] + self.master_data[float(pwm)])
                
                self.get_logger().info(f"SUCCESS: 3-Axis Calibration saved to {save_path}")
                
                if self.auto_apply:
                    msg = String(data=f"CALIB:{save_path}")
                    self.ctrl_pub.publish(msg)
            
            except Exception as e:
                self.get_logger().error(f"Save failed: {e}")

            self.state = 'IDLE'

def main():
    rclpy.init()
    rclpy.spin(AutoSweepNode())