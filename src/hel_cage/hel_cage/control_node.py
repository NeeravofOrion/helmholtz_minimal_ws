#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np
import time

# ==========================================
# ROS 2 OPEN-LOOP CONTROL NODE (RELATIVE DELTA)
# ==========================================
class OpenLoopControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        self.target = np.zeros(3)
        self.current = np.zeros(3)
        self.ambient = np.zeros(3)
        self.control_enabled = False
        
        self.alpha = 0.7  

        self.last_tel_time = time.time()
        self.TIMEOUT_LIMIT = 1.0 

        self.sub_cmd = self.create_subscription(Vector3, 'cmd_B', self.cmd_cb, 10)
        self.sub_tel = self.create_subscription(Vector3, 'telemetry', self.tel_cb, 10)
        self.sub_ctrl = self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)

        self.b_cmd_pub = self.create_publisher(Vector3, 'b_cmd_internal', 10)
        self.error_pub = self.create_publisher(Vector3, 'error', 10)

        self.last_time = self.get_clock().now()
        self.timer = self.create_timer(0.02, self.control_loop)
        
        self.get_logger().info("Relative Open-Loop Node Ready. Equation: Cmd = Target - Ambient")

    def cmd_cb(self, msg):
        self.target = np.array([msg.x, msg.y, msg.z])

    def tel_cb(self, msg):
        self.last_tel_time = time.time() 
        raw_sensor = np.array([msg.x, msg.y, msg.z])
        self.current = (self.alpha * raw_sensor) + ((1.0 - self.alpha) * self.current)
        
        # Track the ambient Earth field ONLY when the coils are inactive
        if not self.control_enabled:
            self.ambient = self.current.copy()

    def ctrl_cb(self, msg):
        cmd = msg.data.strip().upper()
        if cmd == 'START':
            if time.time() - self.last_tel_time > self.TIMEOUT_LIMIT:
                self.get_logger().error("START REJECTED. Sensor connection is absent.")
                return
                
            self.control_enabled = True
            self.get_logger().info(f"Open-Loop ENGAGED. Ambient locked at X:{self.ambient[0]:.2f}, Y:{self.ambient[1]:.2f}, Z:{self.ambient[2]:.2f}")
            
        elif cmd == 'STOP':
            self.control_enabled = False
            self.get_logger().info("Open-Loop STOPPED. Going silent. Feedforward node will manage descent.")

    def control_loop(self):
        if not self.control_enabled:
            return

        if time.time() - self.last_tel_time > self.TIMEOUT_LIMIT:
            self.get_logger().error("CRITICAL: SENSOR SIGNAL LOST. Control node going silent.")
            self.control_enabled = False
            return

        # 1. Delta Math: Required coil flux to bridge the gap from ambient to target
        b_cmd_out = self.target - self.ambient

        # 2. Live Error Calculation (Target - Live Total Field)
        error = self.target - self.current

        err_msg = Vector3(x=float(error[0]), y=float(error[1]), z=float(error[2]))
        self.error_pub.publish(err_msg)

        cmd_msg = Vector3(x=float(b_cmd_out[0]), y=float(b_cmd_out[1]), z=float(b_cmd_out[2]))
        self.b_cmd_pub.publish(cmd_msg)


def main(args=None):
    rclpy.init(args=args)
    node = OpenLoopControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()