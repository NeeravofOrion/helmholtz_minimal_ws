import rclpy
from rclpy.node import Node
import serial
from helmholtz_interfaces.srv import SetPID
from geometry_msgs.msg import Vector3
from std_msgs.msg import String


def build_packet(type_str: str, x: float, y: float, z: float) -> str:
    return f'<{type_str},{x:.4f},{y:.4f},{z:.4f}>\n'


def parse_packet(line: str):
    line = line.strip()
    if not (line.startswith('<') and line.endswith('>')):
        raise ValueError(f'Bad framing: {line}')
    inner = line[1:-1]
    parts = inner.split(',')
    if len(parts) != 4:
        raise ValueError(f'Expected 4 fields, got {len(parts)}')
    return parts[0], float(parts[1]), float(parts[2]), float(parts[3])


class BridgeNode(Node):
    def __init__(self):
        super().__init__('bridge_node')

        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1.0)

        # ===== SUBSCRIPTIONS =====
        self.create_subscription(Vector3, 'cmd_B', self._cmd_cb, 10)
        self.create_subscription(String, 'control_cmd', self._control_cb, 10)

        # ===== PUB =====
        self.telemetry_pub = self.create_publisher(Vector3, 'telemetry', 10)

        # ===== SERVICE =====
        self.create_service(SetPID, 'set_pid', self._pid_cb)

        # ===== TIMER =====
        self.create_timer(0.01, self._read_serial)

        self.get_logger().info('Bridge node ready.')

    # ===== SERIAL SEND =====
    def _send(self, type_str, x, y, z):
        self.ser.write(build_packet(type_str, x, y, z).encode())

    # ===== CMD (DATA CHANNEL) =====
    def _cmd_cb(self, msg: Vector3):
        self._send('CMD', msg.x, msg.y, msg.z)

    # ===== CONTROL CHANNEL =====
    def _control_cb(self, msg: String):
        cmd = msg.data.strip().upper()

        if cmd == "START":
            self._send('START', 0, 0, 0)

        elif cmd == "STOP":
            self._send('STOP', 0, 0, 0)

        else:
            self.get_logger().warn(f'Unknown control command: {cmd}')

    # ===== PID SERVICE =====
    def _pid_cb(self, request, response):
        self._send('PID', request.kp, request.ki, request.kd)
        self.get_logger().info(
            f'PID sent: kp={request.kp} ki={request.ki} kd={request.kd}'
        )
        response.kp_out = request.kp
        response.ki_out = request.ki
        response.kd_out = request.kd
        response.success = True
        return response

    # ===== SERIAL READ =====
    def _read_serial(self):
        while self.ser.in_waiting:
            try:
                line = self.ser.readline().decode(errors='replace').strip()
            except Exception as e:
                self.get_logger().warn(f'Serial read error: {e}')
                return

            if not line:
                continue

            # HARD FILTER
            if not line.startswith('<'):
                continue
            if not line.endswith('>'):
                continue

            try:
                type_str, x, y, z = parse_packet(line)
            except ValueError:
                continue

            self._dispatch(type_str, x, y, z)

    # ===== DISPATCH =====
    def _dispatch(self, type_str, x, y, z):
        if type_str == 'TEL':
            msg = Vector3()
            msg.x, msg.y, msg.z = x, y, z
            self.telemetry_pub.publish(msg)

        elif type_str == 'OUT':
            self.get_logger().info(f'PID OUT: {x:.2f}, {y:.2f}, {z:.2f}')

        else:
            self.get_logger().info(f'Received: {type_str} {x} {y} {z}')


def main(args=None):
    rclpy.init(args=args)
    node = BridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()