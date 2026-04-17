#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np
import csv
import os
import time
from scipy.interpolate import CubicSpline

class FeedforwardNode(Node):
    def __init__(self):
        super().__init__('feedfwd_node')

        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        self.splines = {'x': None, 'y': None, 'z': None}
        
        # Track the absolute min and max magnetic fields the hardware can produce
        self.bounds_b = {'x': (0.0, 0.0), 'y': (0.0, 0.0), 'z': (0.0, 0.0)}

        # --- THE HARDWARE STATE ---
        self.current_pwm = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.target_pwm = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.is_active = False
        self.max_pwm_slew_rate = 80.0 

        # ===== THE INDEPENDENT WATCHDOG =====
        self.last_tel_time = time.time()
        self.TIMEOUT_LIMIT = 1.0
        self.watchdog_tripped = False 

        default_csv_path = os.path.join(self.ws_root, 'calibration_files', 'calibration.csv')
        self.load_csv(default_csv_path)

        # ===== ROS INTERFACES =====
        self.sub_cmd = self.create_subscription(Vector3, 'b_cmd_internal', self.cmd_callback, 10)
        self.sub_ctrl = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        self.sub_tel = self.create_subscription(Vector3, 'telemetry', self.tel_cb, 10)
        
        self.pub = self.create_publisher(Vector3, 'pwm_cmd', 10)
        
        self.last_time = self.get_clock().now()
        self.timer = self.create_timer(0.02, self.hardware_loop)

        self.get_logger().info("Feedforward Node Ready. Unfolded Spline Mapping Active.")

    def load_csv(self, csv_path):
        self.get_logger().info(f"Loading Calibration. Applying 1st-Degree Linear Regression: {csv_path}")
        pwm_raw, bx_raw, by_raw, bz_raw = [], [], [], []

        try:
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        pwm_raw.append(float(row[0]))
                        bx_raw.append(float(row[1]))
                        by_raw.append(float(row[2]))
                        bz_raw.append(float(row[3]))
                    except (IndexError, ValueError):
                        continue

            if not pwm_raw:
                return

            pwm_arr = np.array(pwm_raw)
            bx_arr = np.array(bx_raw)
            by_arr = np.array(by_raw)
            bz_arr = np.array(bz_raw)

            # LINEAR REGRESSION (Line of Best Fit: PWM = m * B + c)
            # np.polyfit(X, Y, 1) forces a strictly straight line.
            
            # X Axis
            coef_x = np.polyfit(bx_arr, pwm_arr, 1)
            self.splines['x'] = np.poly1d(coef_x)
            self.bounds_b['x'] = (np.min(bx_arr), np.max(bx_arr))

            # Y Axis (This will natively handle your inverted Y polarity)
            coef_y = np.polyfit(by_arr, pwm_arr, 1)
            self.splines['y'] = np.poly1d(coef_y)
            self.bounds_b['y'] = (np.min(by_arr), np.max(by_arr))

            # Z Axis
            coef_z = np.polyfit(bz_arr, pwm_arr, 1)
            self.splines['z'] = np.poly1d(coef_z)
            self.bounds_b['z'] = (np.min(bz_arr), np.max(bz_arr))
            
            self.get_logger().info(f"X-Axis Equation: PWM = {coef_x[0]:.2f} * B + {coef_x[1]:.2f}")
            self.get_logger().info(f"Y-Axis Equation: PWM = {coef_y[0]:.2f} * B + {coef_y[1]:.2f}")
            self.get_logger().info(f"Z-Axis Equation: PWM = {coef_z[0]:.2f} * B + {coef_z[1]:.2f}")

        except Exception as e:
            self.get_logger().error(f"Failed to load calibration: {e}")

    def ctrl_cb(self, msg):
        cmd = msg.data.strip()
        if cmd.startswith("CALIB:"):
            self.load_csv(cmd.split(":", 1)[1])
        elif cmd == 'STOP':
            self.target_pwm = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            self.is_active = True
            self.get_logger().info("STOP Commanded. Safely ramping coils down to 0.")

    def tel_cb(self, msg):
        self.last_tel_time = time.time()
        if self.watchdog_tripped:
            self.get_logger().info("SENSOR SIGNAL RESTORED. System returning to nominal standby.")
            self.watchdog_tripped = False

    def calculate_raw_pwm(self, B_cmd, axis):
        """Translates µT directly to positive/negative PWM without manual sign logic."""
        if self.splines[axis] is None:
            return 0.0
            
        # Prevent the spline from mathematically exploding if asked for a field it cannot reach
        min_b, max_b = self.bounds_b[axis]
        safe_b = np.clip(B_cmd, min_b, max_b)
        
        # The spline natively outputs negative PWM for negative fields
        pwm_raw = float(self.splines[axis](safe_b))
        
        # Final hardware limit clamp
        return float(np.clip(pwm_raw, -255.0, 255.0))

    def cmd_callback(self, msg):
        if self.watchdog_tripped:
            return
            
        self.is_active = True
        self.target_pwm['x'] = self.calculate_raw_pwm(msg.x, 'x')
        self.target_pwm['y'] = self.calculate_raw_pwm(msg.y, 'y')
        self.target_pwm['z'] = self.calculate_raw_pwm(msg.z, 'z')

    def hardware_loop(self):
        # === WATCHDOG TRIGGER ===
        if time.time() - self.last_tel_time > self.TIMEOUT_LIMIT:
            if not self.watchdog_tripped:
                self.watchdog_tripped = True
                if self.is_active or any(abs(v) > 0.01 for v in self.current_pwm.values()):
                    self.get_logger().error("SENSOR SIGNAL LOST. Intercepting PID. Safely ramping hardware to 0.")
                    self.is_active = True 
                    self.target_pwm = {'x': 0.0, 'y': 0.0, 'z': 0.0}
                else:
                    self.get_logger().warn("SENSOR SIGNAL LOST. Feedforward node locked in standby.")

        if not self.is_active:
            return

        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now
        
        if dt <= 0: return
        dt = min(dt, 0.02)
        
        max_change = self.max_pwm_slew_rate * dt
        
        out = Vector3()
        moving = False 
        
        for axis in ['x', 'y', 'z']:
            requested_change = self.target_pwm[axis] - self.current_pwm[axis]
            safe_change = np.clip(requested_change, -max_change, max_change)
            self.current_pwm[axis] += safe_change
            
            if abs(self.current_pwm[axis]) > 0.01:
                moving = True

        out.x = float(self.current_pwm['x'])
        out.y = float(self.current_pwm['y'])
        out.z = float(self.current_pwm['z'])
        
        self.pub.publish(out)

        # === STANDBY LATCH ===
        if not moving and all(abs(v) < 0.01 for v in self.target_pwm.values()):
            self.get_logger().info("Hardware zeroed. Standby mode active.")
            self.is_active = False

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