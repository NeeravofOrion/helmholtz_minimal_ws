import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np
import csv
import os


class VariableFieldNode(Node):
    def __init__(self):
        super().__init__('variable_field_node')

        # ===== STATE =====
        self.active = False
        self.t_data = None
        self.bx_data = None
        self.by_data = None
        self.bz_data = None
        self.t_max = 0.0

        # ===== ROS =====
        self.pub = self.create_publisher(Vector3, 'cmd_B', 10)
        self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)

        # ===== TIMING =====
        self.start_time = self.get_clock().now()

        # ===== LOOP =====
        self.dt = 0.02
        self.create_timer(self.dt, self.loop)

    # ================= LOAD CSV =================
    def load_csv(self, path):
        # ===== USE PATH DIRECTLY =====
       
        if not os.path.isabs(path):
            path = os.path.join(
            os.path.expanduser('~/helmholtz_minimal_ws/varf_files'),
            path)
        self.get_logger().info(f"Loading template: {path}")
        self.get_logger().info(f"FINAL PATH USED: {path}")
        t_list, bx_list, by_list, bz_list = [], [], [], []

        try:
            with open(path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        t_list.append(float(row[0]))
                        bx_list.append(float(row[1]))
                        by_list.append(float(row[2]))
                        bz_list.append(float(row[3]))
                    except:
                        continue
        except FileNotFoundError:
            self.get_logger().error("Template CSV not found")
            return False

        if len(t_list) == 0:
            self.get_logger().error("CSV empty or invalid")
            return False

        self.t_data = np.array(t_list)
        self.bx_data = np.array(bx_list)
        self.by_data = np.array(by_list)
        self.bz_data = np.array(bz_list)

        # ===== SORT =====
        idx = np.argsort(self.t_data)
        self.t_data = self.t_data[idx]
        self.bx_data = self.bx_data[idx]
        self.by_data = self.by_data[idx]
        self.bz_data = self.bz_data[idx]

        self.t_max = self.t_data[-1]

        self.get_logger().info(f"Loaded {len(self.t_data)} points")
        return True

    # ================= CONTROL =================
    def ctrl_cb(self, msg):
        cmd = msg.data.strip()
        self.get_logger().info(f"CMD RECEIVED: {msg.data}")

        if cmd.startswith("VAR_START:"):
            path = cmd.split(":", 1)[1]

            success = self.load_csv(path)

            if success:
                self.start_time = self.get_clock().now()
                self.active = True
                self.get_logger().info("Variable field STARTED")
            else:
                self.active = False

        elif cmd == "STOP":
            self.active = False
            self.get_logger().info("Variable field STOPPED")

    # ================= TIME =================
    def get_time(self):
        now = self.get_clock().now()
        return (now - self.start_time).nanoseconds * 1e-9

    # ================= INTERPOLATION =================
    def interpolate(self, t):
        bx = np.interp(t, self.t_data, self.bx_data)
        by = np.interp(t, self.t_data, self.by_data)
        bz = np.interp(t, self.t_data, self.bz_data)
        return bx, by, bz

    # ================= LOOP =================
    def loop(self):
        self.get_logger().info(f"LOOP ACTIVE={self.active}, DATA={self.t_data is not None}")
        if not self.active or self.t_data is None:
            return

        t = self.get_time()

        # avoid divide-by-zero
        if self.t_max <= 0:
            return

        # loop trajectory
        t = t % self.t_max

        bx, by, bz = self.interpolate(t)

        msg = Vector3()
        msg.x = float(bx)
        msg.y = float(by)
        msg.z = float(bz)

        self.pub.publish(msg)


def main():
    rclpy.init()
    node = VariableFieldNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()