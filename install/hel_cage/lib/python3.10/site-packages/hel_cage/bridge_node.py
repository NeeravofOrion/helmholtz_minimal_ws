import rclpy
from rclpy.node import Node
import serial
from geometry_msgs.msg import Vector3


def build_packet(type_str: str, x: float, y: float, z: float) -> str:
    return f'<{type_str},{x:.4f},{y:.4f},{z:.4f}>\n'


def parse_packet(line: str):
    line = line.strip()
    if not (line.startswith('<') and line.endswith('>')):
        raise ValueError
    inner = line[1:-1]
    parts = inner.split(',')
    if len(parts) != 4:
        raise ValueError
    return parts[0], float(parts[1]), float(parts[2]), float(parts[3])


class BridgeNode(Node):
    def __init__(self):
        super().__init__('bridge_node')

        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1.0)

        # ===== INPUT =====
        self.create_subscription(Vector3, 'pwm_cmd', self._pwm_cb, 10)

        # ===== OUTPUT =====
        self.telemetry_pub = self.create_publisher(Vector3, 'telemetry', 10)

        # ===== TIMER =====
        self.create_timer(0.01, self._read_serial)

        self.get_logger().info('Bridge node ready (PC control mode).')

    # ===== SEND PWM ONLY =====
    def _pwm_cb(self, msg: Vector3):
        self.ser.write(build_packet('PWM', msg.x, msg.y, msg.z).encode())

    # ===== READ SERIAL =====
    def _read_serial(self):
        while self.ser.in_waiting:
            try:
                line = self.ser.readline().decode(errors='replace').strip()
            except Exception:
                return

            if not line.startswith('<') or not line.endswith('>'):
                continue

            try:
                type_str, x, y, z = parse_packet(line)
            except:
                continue

            if type_str == 'TEL':
                msg = Vector3()
                msg.x = x
                msg.y = y
                msg.z = z
                self.telemetry_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = BridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()