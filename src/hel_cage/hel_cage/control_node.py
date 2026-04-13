#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np

# ==========================================
# PID STRATEGY (Physics Units: µT)
# ==========================================
class ClassicPIDController:
    def __init__(self):
        # Default gains (Tuned for magnetic flux correction)
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
        """Wipes memory to prevent integral windup on restart."""
        self.integral.fill(0.0)
        self.prev_error.fill(0.0)

    def compute(self, target: np.ndarray, current: np.ndarray, dt: float) -> tuple:
        # 1. Error in Physics Units (µT)
        error = target - current
        
        # 2. PID Math
        self.integral += error * dt
        
        # Anti-windup (prevent math explosions if hardware maxes out)
        self.integral = np.clip(self.integral, -1000.0, 1000.0) 
        
        deriv = (error - self.prev_error) / dt
        self.prev_error = error
        
        # 3. Control Effort (u) in Physics Units (µT)
        u = (self.kp * error) + (self.ki * self.integral) + (self.kd * deriv)
        
        # 4. Final Commanded Magnetic Field (Feedforward baseline + PID correction)
        B_cmd = target + u
        
        return error, B_cmd

# ==========================================
# ROS 2 NODE
# ==========================================
class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        self.controller = ClassicPIDController()

        # State Variables
        self.target = np.zeros(3)
        self.current = np.zeros(3)
        self.control_enabled = False
        
        # EMA smoothing factor for sensor noise (0.0 = ignore new, 1.0 = no filter)
        self.alpha = 0.7  

        # ===== ROS INTERFACES =====
        # Inputs
        self.sub_cmd = self.create_subscription(Vector3, 'cmd_B', self.cmd_cb, 10)
        self.sub_tel = self.create_subscription(Vector3, 'telemetry', self.tel_cb, 10)
        self.sub_ctrl = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)
        self.sub_pid = self.create_subscription(Vector3, 'pid_gain', self.pid_cb, 10)

        # Outputs (Passed to Calibration Node for PWM conversion)
        self.b_cmd_pub = self.create_publisher(Vector3, 'b_cmd_internal', 10)
        self.error_pub = self.create_publisher(Vector3, 'error', 10)

        # 50Hz Control Loop
        self.last_time = self.get_clock().now()
        self.timer = self.create_timer(0.02, self.control_loop)
        
        self.get_logger().info("Control Node Ready. Awaiting 'START' command.")

    def cmd_cb(self, msg):
        self.target = np.array([msg.x, msg.y, msg.z])

    def tel_cb(self, msg):
        raw_sensor = np.array([msg.x, msg.y, msg.z])
        # EMA Filter: smooths out magnetometer jitter before it hits the PID
        self.current = (self.alpha * raw_sensor) + ((1.0 - self.alpha) * self.current)

    def pid_cb(self, msg):
        self.controller.update_gains(msg.x, msg.y, msg.z)
        self.get_logger().info(f"PID Gains Updated -> Kp: {msg.x:.2f}, Ki: {msg.y:.2f}, Kd: {msg.z:.2f}")

    def ctrl_cb(self, msg):
        cmd = msg.data.strip().upper()
        if cmd == 'START':
            self.control_enabled = True
            self.last_time = self.get_clock().now()
            self.controller.reset() # Crucial: clears old windup
            self.get_logger().info("Control Loop ENGAGED.")
            
        elif cmd == 'STOP':
            self.control_enabled = False
            self.b_cmd_pub.publish(Vector3()) # Safely zero out the requested field
            self.get_logger().info("Control Loop STOPPED. Coils zeroed.")

    def control_loop(self):
        if not self.control_enabled:
            return

        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now

        # Failsafe for timing glitches
        if dt <= 0: return
        dt = min(dt, 0.02)

        # Calculate Error and total Commanded Field (Target + PID Effort)
        error, b_cmd_out = self.controller.compute(self.target, self.current, dt)

        # Publish error for GUI monitoring
        err_msg = Vector3(x=float(error[0]), y=float(error[1]), z=float(error[2]))
        self.error_pub.publish(err_msg)

        # Publish internal command to the Calibration Node
        cmd_msg = Vector3(x=float(b_cmd_out[0]), y=float(b_cmd_out[1]), z=float(b_cmd_out[2]))
        self.b_cmd_pub.publish(cmd_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()