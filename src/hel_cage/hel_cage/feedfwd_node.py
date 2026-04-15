#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np
import csv
import os
from scipy.interpolate import CubicSpline

class FeedforwardNode(Node):
    def __init__(self):
        super().__init__('feedfwd_node')

        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        self.splines = {'x': None, 'y': None, 'z': None}
        self.max_b = {'x': 0.0, 'y': 0.0, 'z': 0.0}

        # --- THE HARDWARE STATE ---
        self.current_pwm = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.target_pwm = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.is_active = False
        # Safe Slew Rate (PWM points per second) - PROTECTS THE CYTRON DRIVERS
        self.max_pwm_slew_rate = 80.0 

        default_csv_path = os.path.join(self.ws_root, 'calibration_files', 'calibration.csv')
        self.load_csv(default_csv_path)

        # ===== ROS INTERFACES =====
        self.sub_cmd = self.create_subscription(Vector3, 'b_cmd_internal', self.cmd_callback, 10)
        self.sub_ctrl = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        self.pub = self.create_publisher(Vector3, 'pwm_cmd', 10)
        
        # THE LIFESAVER: Independent Heartbeat Timer (50Hz)
        self.last_time = self.get_clock().now()
        self.timer = self.create_timer(0.02, self.hardware_loop)

        self.get_logger().info("Feedforward Node Ready. Continuous Slew Protection Active.")

    def load_csv(self, csv_path):
        self.get_logger().info(f"Loading Spline calibration: {csv_path}")
        pwm_raw, bx_raw, by_raw, bz_raw = [], [], [], []

        try:
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        pwm_raw.append(abs(float(row[0])))
                        bx_raw.append(abs(float(row[1])))
                        by_raw.append(abs(float(row[2])))
                        bz_raw.append(abs(float(row[3])))
                    except (IndexError, ValueError):
                        continue

            if not pwm_raw:
                return

            amb_x, amb_y, amb_z = bx_raw[0], by_raw[0], bz_raw[0]
            
            bx_clean = [abs(b - amb_x) for b in bx_raw]
            by_clean = [abs(b - amb_y) for b in by_raw]
            bz_clean = [abs(b - amb_z) for b in bz_raw]

            pwm_arr = np.array(pwm_raw)
            bx_arr, by_arr, bz_arr = np.array(bx_clean), np.array(by_clean), np.array(bz_clean)

            # Build Splines
            bx_unique, idx_x = np.unique(bx_arr, return_index=True)
            self.splines['x'] = CubicSpline(bx_unique, pwm_arr[idx_x])
            self.max_b['x'] = bx_unique[-1]

            by_unique, idx_y = np.unique(by_arr, return_index=True)
            self.splines['y'] = CubicSpline(by_unique, pwm_arr[idx_y])
            self.max_b['y'] = by_unique[-1]

            bz_unique, idx_z = np.unique(bz_arr, return_index=True)
            self.splines['z'] = CubicSpline(bz_unique, pwm_arr[idx_z])
            self.max_b['z'] = bz_unique[-1]
            
        except Exception as e:
            self.get_logger().error(f"Failed to load calibration: {e}")

    def ctrl_cb(self, msg):
        cmd = msg.data.strip()
        if cmd.startswith("CALIB:"):
            self.load_csv(cmd.split(":", 1)[1])
        elif cmd == 'STOP':
            # Safely set the TARGET to 0. 
            # The hardware_loop will smoothly decay the current down to this safe target.
            self.target_pwm = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            self.get_logger().info("STOP Commanded. Safely ramping coils down to 0.")

    def calculate_raw_pwm(self, B_cmd, axis):
        """Translates µT to raw target PWM using splines."""
        if self.splines[axis] is None or abs(B_cmd) < 1e-3:
            return 0.0
            
        abs_b = min(abs(B_cmd), self.max_b[axis])
        pwm_raw = float(self.splines[axis](abs_b))
        return float(np.sign(B_cmd) * np.clip(pwm_raw, 0.0, 255.0))

    def cmd_callback(self, msg):
        """Merely updates the TARGET state. Does not touch the hardware directly."""
        self.is_active = True
        self.target_pwm['x'] = self.calculate_raw_pwm(msg.x, 'x')
        self.target_pwm['y'] = self.calculate_raw_pwm(msg.y, 'y')
        self.target_pwm['z'] = self.calculate_raw_pwm(msg.z, 'z')

    def hardware_loop(self):
        # 1. Check if we should even be talking
        if not self.is_active:
            return

        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now
        
        if dt <= 0: return
        dt = min(dt, 0.02)
        
        max_change = self.max_pwm_slew_rate * dt
        
        out = Vector3()
        moving = False # <--- TRACK IF WE ARE STILL AT POWER
        
        for axis in ['x', 'y', 'z']:
            requested_change = self.target_pwm[axis] - self.current_pwm[axis]
            safe_change = np.clip(requested_change, -max_change, max_change)
            self.current_pwm[axis] += safe_change
            
            # Check if any axis still has current flowing
            if abs(self.current_pwm[axis]) > 0.01:
                moving = True

        out.x = float(self.current_pwm['x'])
        out.y = float(self.current_pwm['y'])
        out.z = float(self.current_pwm['z'])
        
        self.pub.publish(out)

        # 2. GO TO SLEEP: If we are at 0 and the target is 0, shut up.
        if not moving and all(abs(v) < 0.01 for v in self.target_pwm.values()):
            self.is_active = False
            self.get_logger().info("Hardware zeroed. Standby mode active.")
def main(args=None):
    rclpy.init(args=args)
    node = FeedforwardNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()