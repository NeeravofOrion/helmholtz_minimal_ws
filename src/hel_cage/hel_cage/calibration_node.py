#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np
import csv
import os

class CalibrationNode(Node):
    def __init__(self):
        super().__init__('calibration_node')

        # ===== WORKSPACE RESOLUTION =====
        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        
        # ===== INDEPENDENT AXIS ARRAYS =====
        # We store separate B (Magnetic Field) and PWM arrays for each axis.
        # This is critical because sensor noise requires independent sorting for interpolation.
        self.B_x = np.array([]); self.PWM_x = np.array([])
        self.B_y = np.array([]); self.PWM_y = np.array([])
        self.B_z = np.array([]); self.PWM_z = np.array([])

        # ===== LOAD DEFAULT (If available) =====
        # Try to load the most recent master calibration if it exists
        self.calib_dir = os.path.join(self.ws_root, 'calibration_files')
        self._load_latest_master()

        # ===== ROS INTERFACES =====
        # Listens for target field commands (µT) from GUI
        self.sub_cmd = self.create_subscription(Vector3, 'cmd_B', self.cmd_callback, 10)
        
        # Listens for file updates from the AutoSweepNode
        self.sub_ctrl = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        
        # Publishes Feedforward base PWM to the Control Node
        self.pub = self.create_publisher(Vector3, 'pwm_base', 10)
        
        self.get_logger().info("3-Axis Feedforward Calibration Node Ready.")

    def _load_latest_master(self):
        """Helper to find and load the newest master_calib file on startup."""
        if not os.path.exists(self.calib_dir):
            return
            
        files = [f for f in os.listdir(self.calib_dir) if f.startswith('master_calib_')]
        if files:
            # Sort by filename (which includes the Unix timestamp) to get the newest
            latest_file = sorted(files)[-1]
            path = os.path.join(self.calib_dir, latest_file)
            self.load_csv(path)
        else:
            self.get_logger().warn("No master calibration files found. Awaiting Auto-Sweep.")

    def load_csv(self, csv_path):
        self.get_logger().info(f"Loading Master Calibration: {csv_path}")

        pwm_raw, bx_raw, by_raw, bz_raw = [], [], [], []

        # ===== READ 4-COLUMN CSV =====
        try:
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        # Format: [PWM, Bx, By, Bz]
                        # We use abs() because the Helmholtz coil response is symmetric
                        pwm_raw.append(abs(float(row[0])))
                        bx_raw.append(abs(float(row[1])))
                        by_raw.append(abs(float(row[2])))
                        bz_raw.append(abs(float(row[3])))
                    except ValueError:
                        continue # Skip header or corrupted rows
                        
            # Convert to numpy arrays for fast math
            pwm_arr = np.array(pwm_raw)
            bx_arr = np.array(bx_raw)
            by_arr = np.array(by_raw)
            bz_arr = np.array(bz_raw)

            # ===== INDEPENDENT SORTING =====
            # np.interp strictly requires the "x" array (the B field) to be monotonically increasing.
            # Because of sensor noise, we MUST sort each axis independently.
            idx_x = np.argsort(bx_arr)
            self.B_x = bx_arr[idx_x]
            self.PWM_x = pwm_arr[idx_x]

            idx_y = np.argsort(by_arr)
            self.B_y = by_arr[idx_y]
            self.PWM_y = pwm_arr[idx_y]

            idx_z = np.argsort(bz_arr)
            self.B_z = bz_arr[idx_z]
            self.PWM_z = pwm_arr[idx_z]

            self.get_logger().info("Successfully built 3-Axis Feedforward interpolation tables.")
            
        except FileNotFoundError:
            self.get_logger().error(f"File not found: {csv_path}")
        except Exception as e:
            self.get_logger().error(f"Failed to load calibration: {e}")

    def ctrl_cb(self, msg):
        """Listens for the automatic broadcast from the Auto-Sweep Node."""
        cmd = msg.data.strip()
        if cmd.startswith("CALIB:"):
            # Extract the file path sent by AutoSweepNode
            path = cmd.split(":", 1)[1]
            self.load_csv(path)

    def interp_signed(self, target_B, B_array, PWM_array):
        """Calculates the required PWM for a requested magnetic field."""
        # Safety catch if tables aren't loaded yet
        if len(B_array) == 0:
            return 0.0
            
        # 1. Grab the direction (+ or -)
        sign = np.sign(target_B)
        
        # 2. Interpolate the magnitude
        # np.interp(target_x, recorded_x, recorded_y)
        pwm_mag = np.interp(abs(target_B), B_array, PWM_array)
        
        # 3. Re-apply direction
        return sign * pwm_mag

    def cmd_callback(self, msg):
        """Fires every time the GUI requests a new magnetic field."""
        out = Vector3()
        
        # Independently calculate feedforward for each axis
        out.x = float(self.interp_signed(msg.x, self.B_x, self.PWM_x))
        out.y = float(self.interp_signed(msg.y, self.B_y, self.PWM_y))
        out.z = float(self.interp_signed(msg.z, self.B_z, self.PWM_z))
        
        # Publish the baseline guess to the PID Control Node
        self.pub.publish(out)

def main(args=None):
    rclpy.init(args=args)
    node = CalibrationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()