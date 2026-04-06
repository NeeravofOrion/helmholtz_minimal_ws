import sys
import math
from collections import deque

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
from helmholtz_interfaces.srv import SetPID

from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg


BUFFER_SIZE = 500


# ================= ROS NODE =================
class GuiNode(Node):
    def __init__(self):
        super().__init__('gui_node')

        self.pub = self.create_publisher(Vector3, 'cmd_B', 10)
        self.ctrl_pub = self.create_publisher(String, 'control_cmd', 10)

        self.sub = self.create_subscription(Vector3, 'telemetry', self.telemetry_cb, 10)
        self.cli = self.create_client(SetPID, 'set_pid')

        self.data_x = deque(maxlen=BUFFER_SIZE)
        self.data_y = deque(maxlen=BUFFER_SIZE)
        self.data_z = deque(maxlen=BUFFER_SIZE)

    def telemetry_cb(self, msg):
        self.data_x.append(msg.x)
        self.data_y.append(msg.y)
        self.data_z.append(msg.z)

        if hasattr(self, 'gui') and self.gui.ambient_active:
            self.gui.ambient_x.append(msg.x)
            self.gui.ambient_y.append(msg.y)
            self.gui.ambient_z.append(msg.z)

    def publish_cmd(self, x, y, z):
        msg = Vector3()
        msg.x = x
        msg.y = y
        msg.z = z
        self.pub.publish(msg)

    def send_control(self, cmd: str):
        msg = String()
        msg.data = cmd
        self.ctrl_pub.publish(msg)

    def call_pid(self, kp, ki, kd):
        if not self.cli.wait_for_service(timeout_sec=1.0):
            print("Service not available")
            return

        req = SetPID.Request()
        req.kp = kp
        req.ki = ki
        req.kd = kd

        future = self.cli.call_async(req)
        future.add_done_callback(self.pid_response)

    def pid_response(self, future):
        try:
            res = future.result()
            print(f"PID set: {res.kp_out}, {res.ki_out}, {res.kd_out}")
        except Exception as e:
            print(f"Service call failed: {e}")


# ================= GUI =================
class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, ros_node):
        super().__init__()

        self.node = ros_node
        self.setWindowTitle("Helmholtz Cage GUI")

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        self.target_x = 0
        self.target_y = 0
        self.target_z = 0

        # -------- CMD INPUT --------
        input_layout = QtWidgets.QHBoxLayout()

        self.bx = QtWidgets.QLineEdit()
        self.by = QtWidgets.QLineEdit()
        self.bz = QtWidgets.QLineEdit()

        self.bx.setPlaceholderText("Bx (µT)")
        self.by.setPlaceholderText("By (µT)")
        self.bz.setPlaceholderText("Bz (µT)")

        send_btn = QtWidgets.QPushButton("Send CMD")
        send_btn.clicked.connect(self.send_cmd)

        zero_btn = QtWidgets.QPushButton("Zero Field")
        zero_btn.clicked.connect(self.zero_field)

        start_btn = QtWidgets.QPushButton("START")
        start_btn.clicked.connect(self.start_system)

        stop_btn = QtWidgets.QPushButton("STOP")
        stop_btn.clicked.connect(self.stop_system)

        input_layout.addWidget(self.bx)
        input_layout.addWidget(self.by)
        input_layout.addWidget(self.bz)
        input_layout.addWidget(send_btn)
        input_layout.addWidget(zero_btn)
        input_layout.addWidget(start_btn)
        input_layout.addWidget(stop_btn)

        # -------- PID --------
        pid_layout = QtWidgets.QHBoxLayout()

        self.kp = QtWidgets.QLineEdit()
        self.ki = QtWidgets.QLineEdit()
        self.kd = QtWidgets.QLineEdit()

        self.kp.setPlaceholderText("Kp")
        self.ki.setPlaceholderText("Ki")
        self.kd.setPlaceholderText("Kd")

        pid_btn = QtWidgets.QPushButton("Set PID")
        pid_btn.clicked.connect(self.set_pid)

        pid_layout.addWidget(self.kp)
        pid_layout.addWidget(self.ki)
        pid_layout.addWidget(self.kd)
        pid_layout.addWidget(pid_btn)

        # -------- AMBIENT --------
        self.ambient_btn = QtWidgets.QPushButton("Measure Ambient (5s)")
        self.ambient_btn.clicked.connect(self.start_ambient)

        self.ambient_label = QtWidgets.QLabel("Ambient: ---")

        # -------- PLOTS --------
        self.plot_widget = pg.GraphicsLayoutWidget()

        self.plot_x = self.plot_widget.addPlot(title="Bx (µT)")
        self.plot_widget.nextRow()
        self.plot_y = self.plot_widget.addPlot(title="By (µT)")
        self.plot_widget.nextRow()
        self.plot_z = self.plot_widget.addPlot(title="Bz (µT)")

        self.curve_x = self.plot_x.plot(pen='r')
        self.curve_y = self.plot_y.plot(pen='g')
        self.curve_z = self.plot_z.plot(pen='b')

        self.target_curve_x = self.plot_x.plot(pen=pg.mkPen('r', style=QtCore.Qt.DashLine))
        self.target_curve_y = self.plot_y.plot(pen=pg.mkPen('g', style=QtCore.Qt.DashLine))
        self.target_curve_z = self.plot_z.plot(pen=pg.mkPen('b', style=QtCore.Qt.DashLine))

        layout.addLayout(input_layout)
        layout.addLayout(pid_layout)
        layout.addWidget(self.ambient_btn)
        layout.addWidget(self.ambient_label)
        layout.addWidget(self.plot_widget)

        central.setLayout(layout)
        self.setCentralWidget(central)

        # -------- AMBIENT STATE --------
        self.ambient_active = False
        self.ambient_x = []
        self.ambient_y = []
        self.ambient_z = []

        self.ambient_timer = QtCore.QTimer()
        self.ambient_timer.setSingleShot(True)
        self.ambient_timer.timeout.connect(self.finish_ambient)

        # -------- TIMER --------
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30)

    # -------- COMMAND --------
    def send_cmd(self):
        try:
            x = float(self.bx.text())
            y = float(self.by.text())
            z = float(self.bz.text())

            self.target_x = x
            self.target_y = y
            self.target_z = z

            self.node.publish_cmd(x, y, z)

        except:
            print("Invalid CMD input")

    def zero_field(self):
        self.target_x = 0
        self.target_y = 0
        self.target_z = 0
        self.node.publish_cmd(0.0, 0.0, 0.0)

    def start_system(self):
        self.node.send_control("START")

    def stop_system(self):
        self.node.send_control("STOP")

        self.target_x = 0
        self.target_y = 0
        self.target_z = 0

    # -------- PID --------
    def set_pid(self):
        try:
            kp = float(self.kp.text())
            ki = float(self.ki.text())
            kd = float(self.kd.text())
            self.node.call_pid(kp, ki, kd)
        except:
            print("Invalid PID input")

    # -------- AMBIENT --------
    def start_ambient(self):
        self.ambient_x.clear()
        self.ambient_y.clear()
        self.ambient_z.clear()

        self.ambient_active = True
        self.ambient_timer.start(5000)

        self.ambient_label.setText("Measuring...")

    def finish_ambient(self):
        self.ambient_active = False

        if len(self.ambient_x) == 0:
            self.ambient_label.setText("No data")
            return

        avg_x = sum(self.ambient_x) / len(self.ambient_x)
        avg_y = sum(self.ambient_y) / len(self.ambient_y)
        avg_z = sum(self.ambient_z) / len(self.ambient_z)

        B = math.sqrt(avg_x**2 + avg_y**2 + avg_z**2)

        self.ambient_label.setText(
            f"Ambient → Bx: {avg_x:.2f} µT | "
            f"By: {avg_y:.2f} µT | "
            f"Bz: {avg_z:.2f} µT | "
            f"|B|: {B:.2f} µT"
        )

    # -------- PLOT --------
    def update_plot(self):
        self.curve_x.setData(self.node.data_x)
        self.curve_y.setData(self.node.data_y)
        self.curve_z.setData(self.node.data_z)

        n = len(self.node.data_x)
        if n > 0:
            self.target_curve_x.setData([self.target_x] * n)
            self.target_curve_y.setData([self.target_y] * n)
            self.target_curve_z.setData([self.target_z] * n)


# ================= MAIN =================
def main():
    rclpy.init()

    node = GuiNode()

    app = QtWidgets.QApplication(sys.argv)
    win = PlotWindow(node)

    node.gui = win

    win.show()

    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: rclpy.spin_once(node, timeout_sec=0))
    timer.start(10)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()