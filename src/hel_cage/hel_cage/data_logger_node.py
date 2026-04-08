import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
import csv
import os
from datetime import datetime
from ament_index_python.packages import get_package_prefix


class DataLogger(Node):
    def __init__(self):
        super().__init__('data_logger')

        # ===== STATE =====
        self.B_target = Vector3()
        self.B_meas = Vector3()
        self.PWM_base = Vector3()
        self.PWM = Vector3()

        # ===== RESOLVE WORKSPACE ROOT =====
        #pkg_prefix = get_package_prefix('hel_cage')
        #ws_root = os.path.abspath(os.path.join(pkg_prefix, '..', '..', '..'))
        ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        # ===== LOG DIRECTORY =====
        log_dir = os.path.join(ws_root, 'result_logs')
        os.makedirs(log_dir, exist_ok=True)

        # ===== FILE SETUP =====
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_{timestamp}.csv"
        self.filepath = os.path.join(log_dir, filename)

        self.file = open(self.filepath, 'w', newline='')
        self.writer = csv.writer(self.file)

        # header
        self.writer.writerow([
            "time",
            "Bx_target", "By_target", "Bz_target",
            "Bx_meas", "By_meas", "Bz_meas",
            "PWM_base_x", "PWM_base_y", "PWM_base_z",
            "PWM_x", "PWM_y", "PWM_z",
            "err_x", "err_y", "err_z"
        ])

        self.get_logger().info(f"Logging to {self.filepath}")

        # ===== SUBS =====
        self.create_subscription(Vector3, 'cmd_B', self.target_cb, 10)
        self.create_subscription(Vector3, 'telemetry', self.meas_cb, 10)
        self.create_subscription(Vector3, 'pwm_base', self.base_cb, 10)
        self.create_subscription(Vector3, 'pwm_cmd', self.pwm_cb, 10)

        # ===== TIMER =====
        self.create_timer(0.05, self.log_data)

    # ===== CALLBACKS =====
    def target_cb(self, msg):
        self.B_target = msg

    def meas_cb(self, msg):
        self.B_meas = msg

    def base_cb(self, msg):
        self.PWM_base = msg

    def pwm_cb(self, msg):
        self.PWM = msg

    # ===== LOGGING =====
    def log_data(self):
        t = self.get_clock().now().nanoseconds * 1e-9

        ex = self.B_target.x - self.B_meas.x
        ey = self.B_target.y - self.B_meas.y
        ez = self.B_target.z - self.B_meas.z

        self.writer.writerow([
            t,
            self.B_target.x, self.B_target.y, self.B_target.z,
            self.B_meas.x, self.B_meas.y, self.B_meas.z,
            self.PWM_base.x, self.PWM_base.y, self.PWM_base.z,
            self.PWM.x, self.PWM.y, self.PWM.z,
            ex, ey, ez
        ])

        self.file.flush()

    def destroy_node(self):
        self.file.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = DataLogger()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()