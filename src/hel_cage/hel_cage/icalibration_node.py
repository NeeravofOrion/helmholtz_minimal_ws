import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np
import csv
import os
from scipy.interpolate import CubicSpline

class CalibrationNode(Node):
    def __init__(self):
        super().__init__('calibration_node')

        # ===== RESOLVE WORKSPACE ROOT =====
        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        
        # Internal Data Setup
        self.spline = None
        self.max_b = 0.0

        default_csv_path = os.path.join(
            self.ws_root,
            'calibration_files',
            'calibration.csv'
        )

        # Load default calibration on startup
        self.load_csv(default_csv_path)

        # ===== ROS INTERFACES =====
        # Listens to the Commanded Field from the PID node
        self.sub_cmd = self.create_subscription(Vector3, 'b_cmd_internal', self.cmd_callback, 10)
        
        # Listens for GUI Calibration Updates
        self.sub_ctrl = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        
        # Publishes the final hardware signal to the Bridge
        self.pub = self.create_publisher(Vector3, 'pwm_cmd', 10)

    def load_csv(self, csv_path):
        self.get_logger().info(f"Loading MATLAB-style calibration file: {csv_path}")

        current_list = []
        raw_field_list = []

        # ===== LOAD CSV =====
        try:
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        # CSV Format: [PWM, Current, Field]
                        I_val = float(row[1])
                        B_val = float(row[2])
                        current_list.append(abs(I_val))
                        raw_field_list.append(abs(B_val))
                    except (IndexError, ValueError):
                        continue
            
            # Remove the Earth's ambient baseline (the first reading)
            ambient_field = raw_field_list[0]
            b_clean_list = [b - ambient_field for b in raw_field_list]

            # Convert to numpy arrays
            I_array = np.array(current_list)
            B_array = np.array(b_clean_list)

            # ===== SORT AND BUILD CUBIC SPLINE =====
            sort_idx = np.argsort(B_array)
            B_sorted = B_array[sort_idx]
            I_sorted = I_array[sort_idx]

            # Create the MATLAB-equivalent spline
            self.spline = CubicSpline(B_sorted, I_sorted)
            self.max_b = B_sorted[-1]  # Store highest field

            self.get_logger().info(f"Spline built with {len(B_sorted)} points. Baseline removed: {ambient_field} µT")
            
        except FileNotFoundError:
            self.get_logger().error(f"Calibration CSV not found at: {csv_path}. Check path.")
        except Exception as e:
            self.get_logger().error(f"Failed to load calibration: {e}")

    def ctrl_cb(self, msg):
        cmd = msg.data.strip()
        # Listen for the CALIB command from the GUI
        if cmd.startswith("CALIB:"):
            path = cmd.split(":", 1)[1]
            self.load_csv(path)

    def calculate_pwm(self, B_cmd):
        if self.spline is None or abs(B_cmd) < 1e-3:
            return 0.0
            
        sign = np.sign(B_cmd)
        abs_b = abs(B_cmd)
        
        # STEP 1: B -> I (Physics to Amps via Spline)
        abs_b = min(abs_b, self.max_b)
        I_req = float(self.spline(abs_b))
        
        # STEP 2: I -> PWM (Amps to Hardware via Quadratic)
        A = -4.3781323
        B_coeff = 62.39827991
        C = 24.39999672
        
        pwm_raw = (A * I_req**2) + (B_coeff * I_req) + C
        
        # Clip to Arduino PWM limits
        pwm_final = np.clip(pwm_raw, 0.0, 255.0)
        
        return float(sign * pwm_final)

    def cmd_callback(self, msg):
        out = Vector3()
        # Process X, Y, Z through the factory
        out.x = self.calculate_pwm(msg.x)
        out.y = self.calculate_pwm(msg.y)
        out.z = self.calculate_pwm(msg.z)
        
        self.pub.publish(out)

def main(args=None):
    rclpy.init(args=args)
    node = CalibrationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()