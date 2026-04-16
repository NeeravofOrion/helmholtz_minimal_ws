import sys
import time
from collections import deque
import subprocess
import sys
import os
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String

from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg


BUFFER_SIZE    = 500
TEL_TIMEOUT    = 4.0   # seconds


# ================= ROS NODE =================
class GuiNode(Node):
    def __init__(self):
        super().__init__('gui_node')

        # ===== PUBLISHERS =====
        self.cmd_pub  = self.create_publisher(Vector3, 'cmd_B',       10)
        self.ctrl_pub = self.create_publisher(String,  'control_cmd', 10)
        self.pid_pub  = self.create_publisher(Vector3, 'pid_gain',    10)

        # ===== SUBSCRIBERS =====
        self.create_subscription(Vector3, 'telemetry',     self.telemetry_cb,     10)
        self.create_subscription(String,  'bridge_status', self.bridge_status_cb, 10)
        self.create_subscription(String,  'sensor_status', self.sensor_status_cb, 10)
        self.create_subscription(Vector3, 'error',         self.error_cb,         10)
        self.create_subscription(Vector3, 'pwm_cmd',       self.pwm_cb,           10)

        # ===== DATA =====
        self.data_x = deque(maxlen=BUFFER_SIZE)
        self.data_y = deque(maxlen=BUFFER_SIZE)
        self.data_z = deque(maxlen=BUFFER_SIZE)

        self.err_x = deque(maxlen=BUFFER_SIZE)
        self.err_y = deque(maxlen=BUFFER_SIZE)
        self.err_z = deque(maxlen=BUFFER_SIZE)

        self.pwm_x = deque(maxlen=BUFFER_SIZE)
        self.pwm_y = deque(maxlen=BUFFER_SIZE)
        self.pwm_z = deque(maxlen=BUFFER_SIZE)
        
        # Ambient Measurement Data
        self.ambient_measuring = False
        self.amb_x = []
        self.amb_y = []
        self.amb_z = []

        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.0

        self.control_active  = False
        self.last_tel_time   = None
        self.serial_status   = 'UNKNOWN'
        self.sensor_status_s = 'UNKNOWN'

    # ===== CALLBACKS =====
    def telemetry_cb(self, msg):
        self.data_x.append(msg.x)
        self.data_y.append(msg.y)
        self.data_z.append(msg.z)
        self.last_tel_time = time.time()
        
        if self.ambient_measuring:
            self.amb_x.append(msg.x)
            self.amb_y.append(msg.y)
            self.amb_z.append(msg.z)
            
        if hasattr(self, 'gui'):
            self.gui.update_rpi_status(True)

    def bridge_status_cb(self, msg):
        self.serial_status = msg.data
        if hasattr(self, 'gui'):
            self.gui.update_serial_status(msg.data == 'SERIAL_OK')

    def sensor_status_cb(self, msg):
        self.sensor_status_s = msg.data
        if hasattr(self, 'gui'):
            self.gui.update_sensor_status(msg.data == 'SENSOR_OK')

    def error_cb(self, msg):
        if not self.control_active:
            return
        self.err_x.append(msg.x)
        self.err_y.append(msg.y)
        self.err_z.append(msg.z)

    def pwm_cb(self, msg):
       #if not self.control_active:
        #    return
        self.pwm_x.append(msg.x)
        self.pwm_y.append(msg.y)
        self.pwm_z.append(msg.z)

    # ===== PUBLISH =====
    def publish_cmd(self, x, y, z):
        self.target_x, self.target_y, self.target_z = x, y, z
        msg = Vector3()
        msg.x, msg.y, msg.z = float(x), float(y), float(z)
        self.cmd_pub.publish(msg)

    def send_control(self, cmd):
        msg = String()
        msg.data = cmd
        self.ctrl_pub.publish(msg)

    def publish_pid(self, kp, ki, kd):
        msg = Vector3()
        msg.x, msg.y, msg.z = float(kp), float(ki), float(kd)
        self.pid_pub.publish(msg)


# ================= STATUS INDICATOR =================
class StatusIndicator(QtWidgets.QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.dot  = QtWidgets.QLabel('●')
        self.dot.setStyleSheet('color: #888; font-size: 14px;')
        self.text = QtWidgets.QLabel(label)
        self.text.setStyleSheet('font-size: 12px;')
        layout.addWidget(self.dot)
        layout.addWidget(self.text)
        self.setLayout(layout)

    def set_ok(self):      self.dot.setStyleSheet('color: #2ecc71; font-size: 14px;')
    def set_error(self):   self.dot.setStyleSheet('color: #e74c3c; font-size: 14px;')
    def set_unknown(self): self.dot.setStyleSheet('color: #888;    font-size: 14px;')


# ================= GUI =================
class PlotWindow(QtWidgets.QMainWindow):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.setWindowTitle('Helmholtz Cage GUI')
        screen = QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # Calculate the exact left half
        half_width = screen_width // 2

        # Set the window position and size (x, y, width, height)
        # x=0, y=0 is the top-left corner of your monitor
        self.setGeometry(0, 0, half_width, screen_height)
        self.resize(1100, 1200)
        self._active_mode = 'constant'
        # -------- AUTO-LAUNCH TOGGLE --------
        
        root = QtWidgets.QWidget()
        root_layout = QtWidgets.QHBoxLayout()
        root_layout.setSpacing(12)
        root.setLayout(root_layout)
        self.setCentralWidget(root)

        # ===================== LEFT PANEL =====================
        left = QtWidgets.QWidget()
        left.setFixedWidth(320)
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setSpacing(10)
        left.setLayout(left_layout)

        # ── Mode toggle ──
        mode_group = QtWidgets.QGroupBox('Mode')
        mode_inner = QtWidgets.QHBoxLayout()
        self.btn_constant = QtWidgets.QPushButton('Constant Field')
        self.btn_variable = QtWidgets.QPushButton('Variable Field')
        self.btn_constant.setCheckable(True)
        self.btn_variable.setCheckable(True)
        self.btn_constant.setChecked(True)
        self.btn_constant.clicked.connect(lambda: self._set_mode('constant'))
        self.btn_variable.clicked.connect(lambda: self._set_mode('variable'))
        mode_inner.addWidget(self.btn_constant)
        mode_inner.addWidget(self.btn_variable)
        mode_group.setLayout(mode_inner)
        left_layout.addWidget(mode_group)

        # ── Ambient Measurement ──
        ambient_group = QtWidgets.QGroupBox('Ambient Measurement')
        ambient_inner = QtWidgets.QVBoxLayout()
        self.btn_ambient = QtWidgets.QPushButton('Measure Ambient (5s)')
        self.btn_ambient.clicked.connect(self.start_ambient_measurement)
        self.lbl_ambient_result = QtWidgets.QLabel('Bx: - | By: - | Bz: -\nB_tot: -')
        self.lbl_ambient_result.setStyleSheet('font-weight: bold; margin-top: 5px;')
        ambient_inner.addWidget(self.btn_ambient)
        ambient_inner.addWidget(self.lbl_ambient_result)
        ambient_group.setLayout(ambient_inner)
        left_layout.addWidget(ambient_group)

        # ── CSV (variable mode only) ──
        self.csv_group = QtWidgets.QGroupBox('Variable Target CSV File')
        csv_inner = QtWidgets.QVBoxLayout()
        csv_row = QtWidgets.QHBoxLayout()
        self.csv_path = QtWidgets.QLineEdit()
        self.csv_path.setPlaceholderText('CSV filename or path')
        browse_btn = QtWidgets.QPushButton('Browse')
        browse_btn.clicked.connect(self._browse_csv)
        csv_row.addWidget(self.csv_path)
        csv_row.addWidget(browse_btn)
        self.var_start_btn = QtWidgets.QPushButton('Start Variable Field')
        self.var_start_btn.clicked.connect(self.start_variable_field)
        csv_inner.addLayout(csv_row)
        csv_inner.addWidget(self.var_start_btn)
        self.csv_group.setLayout(csv_inner)
        self.csv_group.setVisible(False)
        left_layout.addWidget(self.csv_group)
       
        # ── Calibration File ──
        calib_group = QtWidgets.QGroupBox('Calibration File')
        calib_inner = QtWidgets.QVBoxLayout()
        calib_row = QtWidgets.QHBoxLayout()
        
        self.calib_path = QtWidgets.QLineEdit()
        self.calib_path.setPlaceholderText('Default calibration loaded')
        
        calib_browse_btn = QtWidgets.QPushButton('Browse')
        calib_browse_btn.clicked.connect(self._browse_calib)
        
        calib_row.addWidget(self.calib_path)
        calib_row.addWidget(calib_browse_btn)
        
        # 1. The button to load an existing file
        self.calib_load_btn = QtWidgets.QPushButton('Load Calibration')
        self.calib_load_btn.clicked.connect(self.load_calibration)
        
        # 2. ADD THE NEW INITIALIZATION BUTTONS HERE
        self.btn_init_apply = QtWidgets.QPushButton("Run Initialization & Apply")
        self.btn_init_save = QtWidgets.QPushButton("Run Initialization (Save Only)")
        
        # Style them slightly different so they stand out
        self.btn_init_apply.setStyleSheet("background-color: #3498db; color: white;")
        
        # Connect the clicks to your existing functions
        self.btn_init_apply.clicked.connect(self.run_initialization_and_apply)
        self.btn_init_save.clicked.connect(self.run_initialization_save_only)
        
        # Add everything to the layout
        calib_inner.addLayout(calib_row)
        calib_inner.addWidget(self.calib_load_btn)
        calib_inner.addWidget(self.btn_init_apply) # <--- Added to UI
        calib_inner.addWidget(self.btn_init_save)  # <--- Added to UI
        
        calib_group.setLayout(calib_inner)
        left_layout.addWidget(calib_group)

        # ── CMD input ──
        cmd_group = QtWidgets.QGroupBox('Field Command (µT)')
        cmd_inner = QtWidgets.QGridLayout()
        self.bx = QtWidgets.QLineEdit(); self.bx.setPlaceholderText('Bx')
        self.by = QtWidgets.QLineEdit(); self.by.setPlaceholderText('By')
        self.bz = QtWidgets.QLineEdit(); self.bz.setPlaceholderText('Bz')
        send_btn = QtWidgets.QPushButton('Send CMD')
        zero_btn = QtWidgets.QPushButton('Zero')
        send_btn.clicked.connect(self.send_cmd)
        zero_btn.clicked.connect(self.zero_field)
        cmd_inner.addWidget(self.bx,      0, 0)
        cmd_inner.addWidget(self.by,      0, 1)
        cmd_inner.addWidget(self.bz,      0, 2)
        cmd_inner.addWidget(send_btn,     1, 0, 1, 2)
        cmd_inner.addWidget(zero_btn,     1, 2)
        cmd_group.setLayout(cmd_inner)
        left_layout.addWidget(cmd_group)

        # ── START / STOP ──
        ctrl_group = QtWidgets.QGroupBox('Control')
        ctrl_inner = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton('START')
        self.stop_btn  = QtWidgets.QPushButton('STOP')
        self.start_btn.setStyleSheet('background-color: #2ecc71; color: white; font-weight: bold;')
        self.stop_btn.setStyleSheet('background-color:  #e74c3c; color: white; font-weight: bold;')
        self.start_btn.clicked.connect(self.start_system)
        self.stop_btn.clicked.connect(self.stop_system)
        ctrl_inner.addWidget(self.start_btn)
        ctrl_inner.addWidget(self.stop_btn)
        ctrl_group.setLayout(ctrl_inner)
        left_layout.addWidget(ctrl_group)

        # ── PID ──
        pid_group = QtWidgets.QGroupBox('PID Gains')
        pid_inner = QtWidgets.QGridLayout()
        self.kp = QtWidgets.QLineEdit(); self.kp.setPlaceholderText('Kp')
        self.ki = QtWidgets.QLineEdit(); self.ki.setPlaceholderText('Ki')
        self.kd = QtWidgets.QLineEdit(); self.kd.setPlaceholderText('Kd')
        pid_btn = QtWidgets.QPushButton('Set PID')
        pid_btn.clicked.connect(self.set_pid)
        pid_inner.addWidget(self.kp,  0, 0)
        pid_inner.addWidget(self.ki,  0, 1)
        pid_inner.addWidget(self.kd,  0, 2)
        pid_inner.addWidget(pid_btn,  1, 0, 1, 3)
        pid_group.setLayout(pid_inner)
        left_layout.addWidget(pid_group)

        # ── Status ──
        status_group = QtWidgets.QGroupBox('System Status')
        status_inner = QtWidgets.QVBoxLayout()
        self.ind_rpi    = StatusIndicator('RPi / Telemetry')
        self.ind_serial = StatusIndicator('Arduino Serial')
        self.ind_sensor = StatusIndicator('Magnetometer')
        status_inner.addWidget(self.ind_rpi)
        status_inner.addWidget(self.ind_serial)
        status_inner.addWidget(self.ind_sensor)
        status_group.setLayout(status_inner)
        left_layout.addWidget(status_group)
        self.auto_launch_cb = QtWidgets.QCheckBox("Auto-launch Analysis Tool on Exit")
        self.auto_launch_cb.setChecked(False)
        left_layout.addWidget(self.auto_launch_cb)
        left_layout.addStretch()

        # ===================== RIGHT PANEL — PLOTS =====================
        right_layout = QtWidgets.QVBoxLayout()

        # ── Field plots (always visible) ──
        self.field_widget = pg.GraphicsLayoutWidget()
        self.plot_x = self.field_widget.addPlot(title='Bx (µT)')
        self.field_widget.nextRow()
        self.plot_y = self.field_widget.addPlot(title='By (µT)')
        self.field_widget.nextRow()
        self.plot_z = self.field_widget.addPlot(title='Bz (µT)')

        self.curve_x = self.plot_x.plot(pen='r')
        self.curve_y = self.plot_y.plot(pen='g')
        self.curve_z = self.plot_z.plot(pen='b')

        # Target dotted lines — only updated in constant mode
        dash = pg.mkPen('w', style=QtCore.Qt.DashLine, width=1)
        self.target_line_x = self.plot_x.plot(pen=dash)
        self.target_line_y = self.plot_y.plot(pen=dash)
        self.target_line_z = self.plot_z.plot(pen=dash)

        for plot in [self.plot_x, self.plot_y, self.plot_z]:
            plot.setYRange(-280, 280)
            plot.setLimits(yMin=-280, yMax=280)

        right_layout.addWidget(self.field_widget, stretch=3)

        # ── Error + PWM plots (visible only when control active) ──
        self.extra_widget = pg.GraphicsLayoutWidget()

        self.plot_err = self.extra_widget.addPlot(title='Error (µT)')
        self.extra_widget.nextRow()
        self.plot_pwm = self.extra_widget.addPlot(title='PWM Output')

        self.curve_ex = self.plot_err.plot(pen='r',  name='Ex')
        self.curve_ey = self.plot_err.plot(pen='g',  name='Ey')
        self.curve_ez = self.plot_err.plot(pen='b',  name='Ez')

        self.curve_px = self.plot_pwm.plot(pen='r',  name='Px')
        self.curve_py = self.plot_pwm.plot(pen='g',  name='Py')
        self.curve_pz = self.plot_pwm.plot(pen='b',  name='Pz')

        # Error scale: ±50 µT reasonable starting point
        self.plot_err.setYRange(-200, 200)
        self.plot_err.setLimits(yMin=-200, yMax=200)

        # PWM scale: ±260
        self.plot_pwm.setYRange(-260, 260)
        self.plot_pwm.setLimits(yMin=-260, yMax=260)

        self.extra_widget.setVisible(True)
        right_layout.addWidget(self.extra_widget, stretch=2)

        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(right_layout)

        root_layout.addWidget(left)
        root_layout.addWidget(right_widget, stretch=1)

        # ===================== TIMERS =====================
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(30)

        self.status_timer = QtCore.QTimer()
        self.status_timer.timeout.connect(self._check_telemetry_timeout)
        self.status_timer.start(1000)
    
    def closeEvent(self, event):
        """This triggers automatically when you close the GUI window."""
        if hasattr(self, 'auto_launch_cb') and self.auto_launch_cb.isChecked():
            print("Auto-launching Data Analysis Tool...")
            try:
                # FIX: Point directly to your result_logs folder instead of the ROS install folder
                analyzer_path = os.path.expanduser('~/helmholtz_minimal_ws/result_logs/anie.py')
                
                # Double check that the file actually exists before trying to run it
                if not os.path.exists(analyzer_path):
                    print(f"Error: Could not find anie.py at {analyzer_path}")
                else:
                    subprocess.Popen([sys.executable, analyzer_path])
            except Exception as e:
                print(f"Failed to launch analysis tool: {e}")
        else:
            print("Auto-launch disabled. Shutting down cleanly.")
            
        event.accept()
    # ===== FILE PICKERS =====
    def _browse_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select Target CSV File', '', 'CSV Files (*.csv);;All Files (*)'
        )
        if path:
            self.csv_path.setText(path)
            
    def _browse_calib(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select Calibration CSV File', '', 'CSV Files (*.csv);;All Files (*)'
        )
        if path:
            self.calib_path.setText(path)

    # ===== MODE =====
    def _set_mode(self, mode):
        self._active_mode = mode
        self.btn_constant.setChecked(mode == 'constant')
        self.btn_variable.setChecked(mode == 'variable')
        self.csv_group.setVisible(mode == 'variable')
        
    # ===== AMBIENT MEASUREMENT =====
    def start_ambient_measurement(self):
        self.node.amb_x.clear()
        self.node.amb_y.clear()
        self.node.amb_z.clear()
        self.node.ambient_measuring = True
        self.btn_ambient.setText('Measuring... (Wait 5s)')
        self.btn_ambient.setEnabled(False)
        self.lbl_ambient_result.setText('Collecting data...')
        # Call the finish function after 5000 milliseconds
        QtCore.QTimer.singleShot(5000, self.finish_ambient_measurement)

    def finish_ambient_measurement(self):
        self.node.ambient_measuring = False
        self.btn_ambient.setText('Measure Ambient (5s)')
        self.btn_ambient.setEnabled(True)

        if len(self.node.amb_x) == 0:
            self.lbl_ambient_result.setText("No data received!")
            return

        avg_x = sum(self.node.amb_x) / len(self.node.amb_x)
        avg_y = sum(self.node.amb_y) / len(self.node.amb_y)
        avg_z = sum(self.node.amb_z) / len(self.node.amb_z)
        b_tot = (avg_x**2 + avg_y**2 + avg_z**2)**0.5

        self.lbl_ambient_result.setText(
            f'Bx: {avg_x:.2f} | By: {avg_y:.2f} | Bz: {avg_z:.2f}\n'
            f'B_tot: {b_tot:.2f} µT'
        )

    # ===== CALIBRATION =====
    def load_calibration(self):
        path = self.calib_path.text().strip()
        if not path:
            print('Calibration path required')
            return
        self.node.send_control(f'CALIB:{path}')

    # ===== STATUS =====
    def update_rpi_status(self, ok):
        self.ind_rpi.set_ok() if ok else self.ind_rpi.set_error()

    def update_serial_status(self, ok):
        self.ind_serial.set_ok() if ok else self.ind_serial.set_error()

    def update_sensor_status(self, ok):
        self.ind_sensor.set_ok() if ok else self.ind_sensor.set_error()

    def _check_telemetry_timeout(self):
        if self.node.last_tel_time is None:
            self.ind_rpi.set_unknown()
        elif time.time() - self.node.last_tel_time > TEL_TIMEOUT:
            self.ind_rpi.set_error()

    # ===== COMMANDS =====
    def send_cmd(self):
        if self._active_mode != 'constant':
            return
        try:
            x = float(self.bx.text())
            y = float(self.by.text())
            z = float(self.bz.text())
            self.node.publish_cmd(x, y, z)
        except:
            print('Invalid CMD input')

    def zero_field(self):
        if self._active_mode != 'constant':
            return
        self.node.publish_cmd(0.0, 0.0, 0.0)

    def start_system(self):
        if self._active_mode == 'variable':
            return
        self.node.control_active = True
        self.node.err_x.clear(); self.node.err_y.clear(); self.node.err_z.clear()
        #self.node.pwm_x.clear(); self.node.pwm_y.clear(); self.node.pwm_z.clear()
        self.extra_widget.setVisible(True)
        self.node.send_control('START')

    def stop_system(self):
        self.node.control_active = False
        
        self.node.send_control('STOP')

    def start_variable_field(self):
        path = self.csv_path.text().strip()
        if not path:
            print('CSV path required')
            return
        self.node.send_control(f'VAR_START:{path}')
        self.node.send_control('START')

    # ===== PID =====
    def set_pid(self):
        try:
            self.node.publish_pid(
                float(self.kp.text()),
                float(self.ki.text()),
                float(self.kd.text())
            )
        except:
            print('Invalid PID input')

    def run_initialization_and_apply(self):
     """Runs the 0-255 sweep and immediately tells the system to use it."""
     msg = String()
     msg.data = "SWEEP:APPLY"
     self.node.ctrl_pub.publish(msg) 
     print("Sent SWEEP:APPLY command to ROS.")
 
    def run_initialization_save_only(self):
        """Runs the 0-255 sweep but just saves the file; doesn't update live math."""
        msg = String()
        msg.data = "SWEEP:SAVE_ONLY"
        self.node.ctrl_pub.publish(msg)
        print("Sent SWEEP:SAVE_ONLY command to ROS.")

    # ===== PLOT =====
    def update_plot(self):
        self.curve_x.setData(self.node.data_x)
        self.curve_y.setData(self.node.data_y)
        self.curve_z.setData(self.node.data_z)

        # Target lines — constant mode only
        n = len(self.node.data_x)
        if self._active_mode == 'constant' and n > 0:
            self.target_line_x.setData([self.node.target_x] * n)
            self.target_line_y.setData([self.node.target_y] * n)
            self.target_line_z.setData([self.node.target_z] * n)
        else:
            self.target_line_x.setData([])
            self.target_line_y.setData([])
            self.target_line_z.setData([])

        # Error + PWM — only when control active
        if self.node.control_active:
            self.curve_ex.setData(self.node.err_x)
            self.curve_ey.setData(self.node.err_y)
            self.curve_ez.setData(self.node.err_z)
        
        self.curve_px.setData(self.node.pwm_x)
        self.curve_py.setData(self.node.pwm_y)
        self.curve_pz.setData(self.node.pwm_z)  


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