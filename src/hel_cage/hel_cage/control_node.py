import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String


class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        # ===== SUBS =====
        self.create_subscription(Vector3, 'telemetry', self.tel_cb, 10)
        self.create_subscription(Vector3, 'cmd_B', self.cmd_cb, 10)
        self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)

        # ===== PUB =====
        self.pwm_pub = self.create_publisher(Vector3, 'pwm_cmd', 10)

        # ===== STATE =====
        self.target = Vector3()
        self.current = Vector3()

        self.control_enabled = False

        # PID gains
        self.kp = 0.5
        self.ki = 0.0
        self.kd = 0.0

        # PID state
        self.int_x = 0
        self.int_y = 0
        self.int_z = 0

        self.prev_x = 0
        self.prev_y = 0
        self.prev_z = 0

        self.last_time = self.get_clock().now()

    # ===== TELEMETRY =====
    def tel_cb(self, msg: Vector3):
        self.current = msg

        if not self.control_enabled:
            return

        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now

        if dt <= 0:
            return

        # ===== ERROR =====
        ex = self.target.x - self.current.x
        ey = self.target.y - self.current.y
        ez = self.target.z - self.current.z

        # ===== INTEGRAL =====
        self.int_x += ex * dt
        self.int_y += ey * dt
        self.int_z += ez * dt

        # clamp
        self.int_x = max(min(self.int_x, 100), -100)
        self.int_y = max(min(self.int_y, 100), -100)
        self.int_z = max(min(self.int_z, 100), -100)

        # ===== DERIVATIVE =====
        dx = (ex - self.prev_x) / dt
        dy = (ey - self.prev_y) / dt
        dz = (ez - self.prev_z) / dt

        self.prev_x = ex
        self.prev_y = ey
        self.prev_z = ez

        # ===== PID =====
        ux = self.kp * ex + self.ki * self.int_x + self.kd * dx
        uy = self.kp * ey + self.ki * self.int_y + self.kd * dy
        uz = self.kp * ez + self.ki * self.int_z + self.kd * dz

        # ===== CLAMP TO PWM =====
        ux = max(min(ux, 255), -255)
        uy = max(min(uy, 255), -255)
        uz = max(min(uz, 255), -255)

        # ===== PUBLISH =====
        out = Vector3()
        out.x = ux
        out.y = uy
        out.z = uz

        self.pwm_pub.publish(out)

    # ===== TARGET =====
    def cmd_cb(self, msg: Vector3):
        self.target = msg

        # reset PID state
        self.int_x = self.int_y = self.int_z = 0
        self.prev_x = self.prev_y = self.prev_z = 0

    # ===== CONTROL =====
    def ctrl_cb(self, msg: String):
        cmd = msg.data.strip().upper()

        if cmd == "START":
            self.control_enabled = True
            self.last_time = self.get_clock().now()

        elif cmd == "STOP":
            self.control_enabled = False

            # send zero PWM
            zero = Vector3()
            zero.x = 0
            zero.y = 0
            zero.z = 0
            self.pwm_pub.publish(zero)


def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()