import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import csv
import os
from datetime import datetime

class DataLogger(Node):
    def __init__(self):
        super().__init__('data_logger')

        # ===== STATE =====
        self.B_target = Vector3()
        self.B_meas = Vector3()
        self.PWM_base = Vector3()
        self.PWM = Vector3()
        
        # Guard flags
        self.recording_started = False
        self.file = None
        self.writer = None

        # ===== WORKSPACE & PATHS =====
        self.ws_root = os.path.expanduser('~/helmholtz_minimal_ws')
        self.log_dir = os.path.join(self.ws_root, 'result_logs')
        os.makedirs(self.log_dir, exist_ok=True)

        # ===== SUBS =====
        self.create_subscription(Vector3, 'cmd_B', self.target_cb, 10)
        self.create_subscription(Vector3, 'telemetry', self.meas_cb, 10)
        self.create_subscription(Vector3, 'pwm_base', self.base_cb, 10)
        self.create_subscription(Vector3, 'pwm_cmd', self.pwm_cb, 10)
        self.create_subscription(String, 'control_cmd', self.ctrl_cb, 10)

        # ===== TIMER (20Hz) =====
        self.create_timer(0.05, self.log_data)
        self.get_logger().info("Data Logger Ready. Waiting for the FIRST 'START' command...")

    def target_cb(self, msg): self.B_target = msg
    def meas_cb(self, msg):   self.B_meas = msg
    def base_cb(self, msg):   self.PWM_base = msg
    def pwm_cb(self, msg):    self.PWM = msg

    def ctrl_cb(self, msg):
        """Only used to trigger the start of the session."""
        cmd = msg.data.strip().upper()
        
        # Once we start, we don't stop recording until the node dies.
        if cmd == 'START' and not self.recording_started:
            self._initialize_session()

    def _initialize_session(self):
        """Creates the file once per node lifecycle."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_log_{timestamp}.csv"
        filepath = os.path.join(self.log_dir, filename)

        try:
            self.file = open(filepath, 'w', newline='')
            self.writer = csv.writer(self.file)
            
            self.writer.writerow([
                "time",
                "Bx_target", "By_target", "Bz_target",
                "Bx_meas", "By_meas", "Bz_meas",
                "PWM_base_x", "PWM_base_y", "PWM_base_z",
                "PWM_x", "PWM_y", "PWM_z",
                "err_x", "err_y", "err_z"
            ])
            
            self.recording_started = True
            self.get_logger().info(f"SESSION RECORDING STARTED: {filepath}")
        except Exception as e:
            self.get_logger().error(f"Failed to create log file: {e}")

    def log_data(self):
        # We only record if the first START has been clicked
        if not self.recording_started or self.writer is None:
            return

        t = self.get_clock().now().nanoseconds * 1e-9

        # Calculate error (useful to see error spikes even when STOP is clicked)
        ex = self.B_target.x - self.B_meas.x
        ey = self.B_target.y - self.B_meas.y
        ez = self.B_target.z - self.B_meas.z

        self.writer.writerow([
            t,
            self.B_target.x, self.B_target.y, self.B_target.z,
            self.B_meas.x, self.B_meas.y, self.B_meas.z,
            self.PWM_base.x, self.PWM_base.y, self.PWM_base.z,
            self.PWM.x, self.PWM.y, self.PWM.z,
            ex, ey, ez
        ])
        
        # Flush regularly to ensure data is saved if the GUI is killed
        self.file.flush()

    def destroy_node(self):
        """The only place where the file is officially closed."""
        if self.file:
            self.get_logger().info("Closing session log file...")
            self.file.flush()
            self.file.close()
        super().destroy_node()

def main():
    rclpy.init()
    node = DataLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()