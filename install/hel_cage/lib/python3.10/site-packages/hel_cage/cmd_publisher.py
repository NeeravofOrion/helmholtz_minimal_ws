import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3


class CmdPublisher(Node):
    def __init__(self):
        super().__init__('cmd_publisher')

        self.pub = self.create_publisher(Vector3, 'cmd_B', 10)

        self.msg = Vector3()  # stored command

        # timer every 2 seconds
        self.timer = self.create_timer(2.0, self.publish_cmd)

        # take initial input
        self.get_input()

    def get_input(self):
        while True:
            try:
                raw = input("Enter Bx By Bz: ")
                parts = raw.strip().split()

                if len(parts) != 3:
                    print("Invalid input. Use: x y z")
                    continue

                x, y, z = map(float, parts)

                self.msg.x = x
                self.msg.y = y
                self.msg.z = z

                print(f"Stored: {x}, {y}, {z}")
                break

            except Exception as e:
                print(f"Error: {e}")

    def publish_cmd(self):
        self.pub.publish(self.msg)
        print(f"Published: {self.msg.x}, {self.msg.y}, {self.msg.z}")


def main(args=None):
    rclpy.init(args=args)
    node = CmdPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()