import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np
import csv
import os
from ament_index_python.packages import get_package_prefix


class CalibrationNode(Node):
    def __init__(self):
        super().__init__('calibration_node')

        # ===== RESOLVE WORKSPACE ROOT =====
        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        
        # Internal Data Setup
        self.B_data = np.array([])
        self.PWM_data = np.array([])

        default_csv_path = os.path.join(
            self.ws_root,
            'calibration_files',
            'calibration.csv'
        )

        # Load default calibration on startup
        self.load_csv(default_csv_path)

        # ===== ROS INTERFACES =====
        self.sub_cmd = self.create_subscription(Vector3, 'cmd_B', self.cmd_callback, 10)
        self.sub_ctrl = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        self.pub = self.create_publisher(Vector3, 'pwm_base', 10)

    def load_csv(self, csv_path):
        self.get_logger().info(f"Loading calibration file: {csv_path}")

        pwm_list = []
        B_list = []

        # ===== LOAD CSV =====
        try:
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        pwm = float(row[0])
                        B = float(row[1])
                        pwm_list.append(abs(pwm))
                        B_list.append(abs(B))
                    except:
                        continue
                        
            pwm_array = np.array(pwm_list)
            B_array = np.array(B_list)

            # ===== SORT FOR INTERPOLATION =====
            sort_idx = np.argsort(B_array)
            self.B_data = B_array[sort_idx]
            self.PWM_data = pwm_array[sort_idx]

            self.get_logger().info(f"Loaded {len(self.B_data)} calibration points")
            
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

    def interp_signed(self, B):
        # Prevent crash if data is completely empty due to a bad path
        if len(self.B_data) == 0:
            return 0.0
            
        sign = np.sign(B)
        pwm_mag = np.interp(abs(B), self.B_data, self.PWM_data)
        return sign * pwm_mag

    def cmd_callback(self, msg):
        out = Vector3()
        out.x = float(self.interp_signed(msg.x))
        out.y = float(self.interp_signed(msg.y))
        out.z = float(self.interp_signed(msg.z))
        self.pub.publish(out)


def main():
    rclpy.init()
    node = CalibrationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()