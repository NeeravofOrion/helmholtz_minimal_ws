import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
import numpy as np
import csv
import os
from ament_index_python.packages import get_package_prefix


class CalibrationNode(Node):
    def __init__(self):
        super().__init__('calibration_node')

        # ===== RESOLVE WORKSPACE ROOT =====
        #pkg_prefix = get_package_prefix('hel_cage')
        #ws_root = os.path.abspath(os.path.join(pkg_prefix, '..', '..', '..'))
        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')

        csv_path = os.path.join(
    self.ws_root,
    'calibration_files',
    'calibration.csv'
)
        # ===== BUILD CSV PATH =====
        #csv_path = os.path.join(ws_root, 'calibration_files', 'calibration.csv')

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
        except FileNotFoundError:
            self.get_logger().error("Calibration CSV not found. Check path.")
            raise

        pwm_array = np.array(pwm_list)
        B_array = np.array(B_list)

        # ===== SORT FOR INTERPOLATION =====
        sort_idx = np.argsort(B_array)
        self.B_data = B_array[sort_idx]
        self.PWM_data = pwm_array[sort_idx]

        self.get_logger().info(f"Loaded {len(self.B_data)} calibration points")

        # ===== ROS INTERFACES =====
        self.sub = self.create_subscription(Vector3, 'cmd_B', self.callback, 10)
        self.pub = self.create_publisher(Vector3, 'pwm_base', 10)

    def interp_signed(self, B):
        sign = np.sign(B)
        pwm_mag = np.interp(abs(B), self.B_data, self.PWM_data)
        return sign * pwm_mag

    def callback(self, msg):
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