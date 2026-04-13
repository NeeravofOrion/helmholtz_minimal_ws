import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np

# ==========================================
# SUPERVISOR'S MATLAB PID STRATEGY
# ==========================================
class ClassicPIDController:
    def __init__(self):
        # Default gains from MATLAB PARAM.Kp_default
        self.kp = 1.2784
        self.ki = 0.5 
        self.kd = 0.0
        
        self.integral = np.zeros(3)
        self.prev_error = np.zeros(3)

    def update_gains(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def reset(self):
        self.integral.fill(0.0)
        self.prev_error.fill(0.0)

    def compute(self, target: np.ndarray, current: np.ndarray, dt: float) -> tuple:
        # 1. Error in Physics Units (µT)
        error = target - current
        
        # 2. PID Math
        self.integral += error * dt
        # Anti-windup (prevent math explosions)
        self.integral = np.clip(self.integral, -1000, 1000) 
        
        deriv = (error - self.prev_error) / dt
        self.prev_error = error
        
        # 3. Control Effort (u) in Physics Units (µT)
        u = (self.kp * error) + (self.ki * self.integral) + (self.kd * deriv)
        
        # 4. Final Commanded Magnetic Field
        B_cmd = target + u
        return error, B_cmd

# ==========================================
# ROS NODE
# ==========================================
class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        self.controller = ClassicPIDController()

        # State Variables
        self.target = np.zeros(3)
        self.current = np.zeros(3)
        self.control_enabled = False
        self.alpha = 0.7  # EMA smoothing factor for sensor noise

        # ROS Interfaces
        self.sub_cmd = self.create_subscription(Vector3, 'cmd_B', self.cmd_cb, 10)
        self.sub_tel = self.create_subscription(Vector3, 'telemetry', self.tel_cb, 10)
        self.sub_ctrl = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        self.sub_pid = self.create_subscription(Vector3, 'pid_gain', self.pid_cb, 10)

        # OUTPUT: Commanded Field (Passed to Calibration), NOT PWM!
        self.b_cmd_pub = self.create_publisher(Vector3, 'b_cmd_internal', 10)
        self.error_pub = self.create_publisher(Vector3, 'error', 10)

        self.last_time = self.get_clock().now()
        self.timer = self.create_timer(0.02, self.control_loop)  # 50Hz

    def cmd_cb(self, msg):
        self.target = np.array([msg.x, msg.y, msg.z])

    def tel_cb(self, msg):
        raw_sensor = np.array([msg.x, msg.y, msg.z])
        # EMA Filter: (alpha * new) + ((1 - alpha) * old)
        self.current = (self.alpha * raw_sensor) + ((1.0 - self.alpha) * self.current)

    def pid_cb(self, msg):
        self.controller.update_gains(msg.x, msg.y, msg.z)

    def ctrl_cb(self, msg):
        cmd = msg.data.strip()
        if cmd == 'START':
            self.control_enabled = True
            self.last_time = self.get_clock().now()
            self.controller.reset()
        elif cmd == 'STOP':
            self.control_enabled = False
            self.b_cmd_pub.publish(Vector3()) # Send zero field

    def control_loop(self):
        if not self.control_enabled:
            return

        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now

        if dt <= 0: return
        dt = min(dt, 0.02)

        # Calculate Error and Commanded Field
        error, b_cmd_out = self.controller.compute(self.target, self.current, dt)

        # Publish error to GUI
        err_msg = Vector3(x=float(error[0]), y=float(error[1]), z=float(error[2]))
        self.error_pub.publish(err_msg)

        # Publish Commanded Field to Calibration Node
        cmd_msg = Vector3(x=float(b_cmd_out[0]), y=float(b_cmd_out[1]), z=float(b_cmd_out[2]))
        self.b_cmd_pub.publish(cmd_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()