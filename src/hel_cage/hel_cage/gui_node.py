import sys
import math
from collections import deque

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String

from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg


BUFFER_SIZE = 500


# ================= ROS NODE =================
class GuiNode(Node):
    def __init__(self):
        super().__init__('gui_node')

        self.cmd_pub = self.create_publisher(Vector3, 'cmd_B', 10)
        self.ctrl_pub = self.create_publisher(String, 'control_cmd', 10)
        self.pid_pub = self.create_publisher(Vector3, 'pid_gain', 10)

        self.sub = self.create_subscription(Vector3, 'telemetry', self.telemetry_cb, 10)
        self.state_sub = self.create_subscription(String, 'control_state', self.state_cb, 10)

        self.current_mode = "UNKNOWN"

        self.data_x = deque(maxlen=BUFFER_SIZE)
        self.data_y = deque(maxlen=BUFFER_SIZE)
        self.data_z = deque(maxlen=BUFFER_SIZE)

    def telemetry_cb(self, msg):
        self.data_x.append(msg.x)
        self.data_y.append(msg.y)
        self.data_z.append(msg.z)

    def state_cb(self, msg):
        self.current_mode = msg.data
        if hasattr(self, 'gui'):
            self.gui.update_mode_display(msg.data)

    def publish_cmd(self, x, y, z):
        msg = Vector3()
        msg.x = float(x)
        msg.y = float(y)
        msg.z = float(z)
        self.cmd_pub.publish(msg)

    def send_control(self, cmd):
        msg = String()
        msg.data = cmd
        self.ctrl_pub.publish(msg)

    def publish_pid(self, kp, ki, kd):
        msg = Vector3()
        msg.x = float(kp)
        msg.y = float(ki)
        msg.z = float(kd)
        self.pid_pub.publish(msg)


# ================= GUI =================
class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, node):
        super().__init__()
        self.node = node

        self.setWindowTitle("Helmholtz Cage GUI")

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # ===== MODE DISPLAY =====
        self.mode_label = QtWidgets.QLabel("Mode: UNKNOWN")
        layout.addWidget(self.mode_label)

        # ===== MODE CONTROL =====
        mode_layout = QtWidgets.QHBoxLayout()

        self.mode_selector = QtWidgets.QComboBox()
        self.mode_selector.addItems(["Constant Field", "Variable Field"])

        self.csv_path = QtWidgets.QLineEdit()
        self.csv_path.setPlaceholderText("CSV file")

        self.var_start_btn = QtWidgets.QPushButton("Start Variable Field")
        self.var_start_btn.clicked.connect(self.start_variable_field)

        mode_layout.addWidget(self.mode_selector)
        mode_layout.addWidget(self.csv_path)
        mode_layout.addWidget(self.var_start_btn)

        # ===== CMD INPUT =====
        input_layout = QtWidgets.QHBoxLayout()

        self.bx = QtWidgets.QLineEdit()
        self.by = QtWidgets.QLineEdit()
        self.bz = QtWidgets.QLineEdit()

        self.bx.setPlaceholderText("Bx")
        self.by.setPlaceholderText("By")
        self.bz.setPlaceholderText("Bz")

        send_btn = QtWidgets.QPushButton("Send CMD")
        send_btn.clicked.connect(self.send_cmd)

        zero_btn = QtWidgets.QPushButton("Zero")
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

        # ===== PID CONTROL (RESTORED) =====
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

        # ===== PLOTS =====
        self.plot_widget = pg.GraphicsLayoutWidget()

        self.plot_x = self.plot_widget.addPlot(title="Bx")
        self.plot_widget.nextRow()
        self.plot_y = self.plot_widget.addPlot(title="By")
        self.plot_widget.nextRow()
        self.plot_z = self.plot_widget.addPlot(title="Bz")

        self.curve_x = self.plot_x.plot(pen='r')
        self.curve_y = self.plot_y.plot(pen='g')
        self.curve_z = self.plot_z.plot(pen='b')

        layout.addLayout(mode_layout)
        layout.addLayout(input_layout)
        layout.addLayout(pid_layout)
        layout.addWidget(self.plot_widget)

        central.setLayout(layout)
        self.setCentralWidget(central)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30)

    # ===== MODE DISPLAY =====
    def update_mode_display(self, mode):
        self.mode_label.setText(f"Mode: {mode}")

    # ===== COMMAND =====
    def send_cmd(self):
        if self.mode_selector.currentText() != "Constant Field":
            print("Blocked: Variable mode active")
            return

        try:
            x = float(self.bx.text())
            y = float(self.by.text())
            z = float(self.bz.text())

            self.node.publish_cmd(x, y, z)
        except:
            print("Invalid input")

    def zero_field(self):
        if self.mode_selector.currentText() != "Constant Field":
            return
        self.node.publish_cmd(0, 0, 0)

    def start_system(self):
        if self.mode_selector.currentText() == "Variable Field":
            return
        self.node.send_control("START")
        

    def stop_system(self):
        self.node.send_control("STOP")

    def start_variable_field(self):
     if self.mode_selector.currentText() != "Variable Field":
        return

     path = self.csv_path.text().strip()
     if path == "":
        print("CSV required")
        return

     # 1. Start variable field FIRST (defines cmd_B)
     self.node.send_control(f"VAR_START:{path}")

     # 2. THEN enable control loop
     self.node.send_control("START")

    # ===== PID =====
    def set_pid(self):
        try:
            kp = float(self.kp.text())
            ki = float(self.ki.text())
            kd = float(self.kd.text())
            self.node.publish_pid(kp, ki, kd)
        except:
            print("Invalid PID")

    # ===== PLOT =====
    def update_plot(self):
        self.curve_x.setData(self.node.data_x)
        self.curve_y.setData(self.node.data_y)
        self.curve_z.setData(self.node.data_z)


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