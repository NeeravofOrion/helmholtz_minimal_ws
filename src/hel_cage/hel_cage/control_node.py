import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np


class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        # ===== SUBS =====
        self.create_subscription(Vector3, 'telemetry',    self.tel_cb,  10)
        self.create_subscription(Vector3, 'cmd_B',        self.cmd_cb,  10)
        self.create_subscription(String,  'control_cmd',  self.ctrl_cb, 10)
        self.create_subscription(Vector3, 'pid_gain',     self.pid_cb,  10)
        self.create_subscription(Vector3, 'pwm_base',     self.base_cb, 10)

        # ===== PUBS =====
        self.pwm_pub   = self.create_publisher(Vector3, 'pwm_cmd', 10)
        self.error_pub = self.create_publisher(Vector3, 'error',   10)

        # ===== STATE =====
        self.target  = Vector3()
        self.current = Vector3()
        self.control_enabled = False

        # ===== CALIBRATION BASE =====
        self.pwm_base = np.array([0.0, 0.0, 0.0])

        # ===== PID GAINS =====
        self.kp = 0.2
        self.ki = 0.0
        self.kd = 0.0

        # ===== PID STATE =====
        self.int_x = self.int_y = self.int_z = 0.0
        self.prev_x = self.prev_y = self.prev_z = 0.0
        self.d_x = self.d_y = self.d_z = 0.0

        # ===== TIMING =====
        self.last_time = self.get_clock().now()
        self.last_log  = self.get_clock().now()

        self.create_timer(0.02, self.control_loop)

    # ===== CALLBACKS =====
    def tel_cb(self, msg: Vector3):
        self.current = msg

    def cmd_cb(self, msg: Vector3):
        self.target = msg
        self.int_x = self.int_y = self.int_z = 0.0
        self.prev_x = self.prev_y = self.prev_z = 0.0

    def pid_cb(self, msg: Vector3):
        self.kp = msg.x
        self.ki = msg.y
        self.kd = msg.z

    def base_cb(self, msg: Vector3):
        self.pwm_base = np.array([msg.x, msg.y, msg.z])

    def ctrl_cb(self, msg: String):
        cmd = msg.data.strip().upper()
        if cmd == 'START':
            self.control_enabled = True
            self.last_time = self.get_clock().now()
        elif cmd == 'STOP':
            self.control_enabled = False
            zero = Vector3()
            self.pwm_pub.publish(zero)

    # ===== CONTROL LOOP =====
    def control_loop(self):
        if not self.control_enabled:
            return

        now = self.get_clock().now()
        dt  = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now

        if dt <= 0:
            return
        dt = min(dt, 0.02)

        ex = self.target.x - self.current.x
        ey = self.target.y - self.current.y
        ez = self.target.z - self.current.z

        # DEADBAND
        DB = 0.5
        if abs(ex) < DB: ex = 0.0
        if abs(ey) < DB: ey = 0.0
        if abs(ez) < DB: ez = 0.0

        # Publish error
        err_msg = Vector3()
        err_msg.x, err_msg.y, err_msg.z = ex, ey, ez
        self.error_pub.publish(err_msg)

        # INTEGRAL
        self.int_x = max(min(self.int_x + ex * dt, 100), -100)
        self.int_y = max(min(self.int_y + ey * dt, 100), -100)
        self.int_z = max(min(self.int_z + ez * dt, 100), -100)

        # DERIVATIVE (filtered)
        alpha = 0.2
        self.d_x = alpha * (ex - self.prev_x) / dt + (1 - alpha) * self.d_x
        self.d_y = alpha * (ey - self.prev_y) / dt + (1 - alpha) * self.d_y
        self.d_z = alpha * (ez - self.prev_z) / dt + (1 - alpha) * self.d_z

        self.prev_x = ex
        self.prev_y = ey
        self.prev_z = ez

        # PID OUTPUT
        cx = self.kp * ex + self.ki * self.int_x + self.kd * self.d_x
        cy = self.kp * ey + self.ki * self.int_y + self.kd * self.d_y
        cz = self.kp * ez + self.ki * self.int_z + self.kd * self.d_z

        ux = max(min(self.pwm_base[0] + cx, 255), -255)
        uy = max(min(self.pwm_base[1] + cy, 255), -255)
        uz = max(min(self.pwm_base[2] + cz, 255), -255)

        out = Vector3()
        out.x, out.y, out.z = float(ux), float(uy), float(uz)
        self.pwm_pub.publish(out)

        if (now - self.last_log).nanoseconds > 200_000_000:
            self.get_logger().info(
                f'ERR: {ex:.2f},{ey:.2f},{ez:.2f} | PWM: {ux:.2f},{uy:.2f},{uz:.2f}'
            )
            self.last_log = now


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()