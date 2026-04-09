import rclpy
from rclpy.node import Node
import serial
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
 
 
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
 
        # ===== SERIAL =====
        self._serial_ok = False
        try:
            self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1.0)
            self._serial_ok = True
            self.get_logger().info('Serial connected.')
        except Exception as e:
            self.ser = None
            self.get_logger().error(f'Serial failed: {e}')
 
        # ===== LAST TEL TIME =====
        self._last_tel_time = None
        self._sensor_timeout = 2.0  # seconds with no TEL = sensor dead
 
        # ===== SUBS =====
        self.create_subscription(Vector3, 'pwm_cmd', self._pwm_cb, 10)
 
        # ===== PUBS =====
        self.telemetry_pub    = self.create_publisher(Vector3, 'telemetry', 10)
        self.bridge_status_pub = self.create_publisher(String, 'bridge_status', 10)
        self.sensor_status_pub = self.create_publisher(String, 'sensor_status', 10)
 
        # ===== TIMERS =====
        self.create_timer(0.01, self._read_serial)   # serial read at 100Hz
        self.create_timer(2.0,  self._publish_status) # status every 2s
 
        self.get_logger().info('Bridge node ready.')
 
    # ===== SEND PWM =====
    def _pwm_cb(self, msg: Vector3):
        if self.ser is None or not self._serial_ok:
            return
        try:
            self.ser.write(build_packet('PWM', msg.x, msg.y, msg.z).encode())
        except Exception as e:
            self._serial_ok = False
            self.get_logger().error(f'Serial write error: {e}')
 
    # ===== READ SERIAL =====
    def _read_serial(self):
        if self.ser is None:
            return
        try:
            while self.ser.in_waiting:
                line = self.ser.readline().decode(errors='replace').strip()
                if not line.startswith('<') or not line.endswith('>'):
                    continue
                try:
                    type_str, x, y, z = parse_packet(line)
                except:
                    continue
 
                if type_str == 'TEL':
                    msg = Vector3()
                    msg.x, msg.y, msg.z = x, y, z
                    self.telemetry_pub.publish(msg)
                    self._last_tel_time = self.get_clock().now()
                    self._serial_ok = True
 
        except Exception as e:
            self._serial_ok = False
            self.get_logger().error(f'Serial read error: {e}')
 
    # ===== PUBLISH STATUS =====
    def _publish_status(self):
        # Serial status
        serial_msg = String()
        serial_msg.data = 'SERIAL_OK' if self._serial_ok else 'SERIAL_ERROR'
        self.bridge_status_pub.publish(serial_msg)
 
        # Sensor status — check if TEL arrived within timeout
        sensor_msg = String()
        if self._last_tel_time is None:
            sensor_msg.data = 'SENSOR_TIMEOUT'
        else:
            elapsed = (self.get_clock().now() - self._last_tel_time).nanoseconds * 1e-9
            sensor_msg.data = 'SENSOR_OK' if elapsed < self._sensor_timeout else 'SENSOR_TIMEOUT'
        self.sensor_status_pub.publish(sensor_msg)
 
        #self.get_logger().info(f'{serial_msg.data} | {sensor_msg.data}')
 
 
def main(args=None):
    rclpy.init(args=args)
    node = BridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
 
 
if __name__ == '__main__':
    main()