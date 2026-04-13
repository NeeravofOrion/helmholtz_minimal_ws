
import sys
import os
import pandas as pd
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# ================= STATUS INDICATOR =================
class StatusIndicator(QtWidgets.QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.dot = QtWidgets.QLabel('●')
        self.set_color('grey')
        
        self.text = QtWidgets.QLabel(label)
        self.text.setStyleSheet('font-size: 14px;')
        
        layout.addWidget(self.dot)
        layout.addWidget(self.text)
        layout.addStretch()
        self.setLayout(layout)

    def set_color(self, color):
        colors = {'grey': '#888888', 'green': '#2ecc71', 'red': '#e74c3c'}
        hex_color = colors.get(color, '#888888')
        self.dot.setStyleSheet(f'color: {hex_color}; font-size: 18px;')

# ================= MATPLOTLIB CANVAS =================
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # Create a 2x3 grid for the 5 plots
        self.axes = [
            self.fig.add_subplot(2, 3, 1), # Tracking
            self.fig.add_subplot(2, 3, 2), # Error
            self.fig.add_subplot(2, 3, 3), # PWM Output
            self.fig.add_subplot(2, 3, 4), # PWM base vs PWM
            self.fig.add_subplot(2, 3, 5)  # Error Magnitude
        ]
        self.fig.tight_layout(pad=3.0)
        super(MplCanvas, self).__init__(self.fig)

# ================= MAIN APPLICATION =================
class DataAnalysisTool(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Helmholtz Cage Data Analysis Tool")
        self.resize(1500, 1500)

        # Main Layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # ===== LEFT PANEL (CONTROLS) =====
        left_panel = QtWidgets.QWidget()
        left_panel.setFixedWidth(300)
        left_layout = QtWidgets.QVBoxLayout(left_panel)

        title = QtWidgets.QLabel("Data Analysis Tool")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(title)

        # --- CSV Status ---
        self.status_ind = StatusIndicator("CSV Status: Unloaded")
        left_layout.addWidget(self.status_ind)

        # --- PID Auto Tune ---
        pid_group = QtWidgets.QGroupBox("1. PID Auto-Tune")
        pid_layout = QtWidgets.QVBoxLayout()
        self.btn_pid = QtWidgets.QPushButton("Load CSV & Tune PID")
        self.btn_pid.clicked.connect(self.run_pid_tune)
        self.lbl_pid_out = QtWidgets.QLabel("Suggested Kp: --\nSuggested Ki: --")
        pid_layout.addWidget(self.btn_pid)
        pid_layout.addWidget(self.lbl_pid_out)
        pid_group.setLayout(pid_layout)
        left_layout.addWidget(pid_group)

        # --- Generate TF ---
        tf_group = QtWidgets.QGroupBox("2. Generate TF (Step Response)")
        tf_layout = QtWidgets.QVBoxLayout()
        tf_warn = QtWidgets.QLabel("⚠️ Requires a Step Response CSV!")
        tf_warn.setStyleSheet("color: #e67e22; font-size: 11px;")
        self.btn_tf = QtWidgets.QPushButton("Load CSV & Gen TF")
        self.btn_tf.clicked.connect(self.run_generate_tf)
        self.lbl_tf_out = QtWidgets.QLabel("Gx: --\nGy: --\nGz: --")
        tf_layout.addWidget(tf_warn)
        tf_layout.addWidget(self.btn_tf)
        tf_layout.addWidget(self.lbl_tf_out)
        tf_group.setLayout(tf_layout)
        left_layout.addWidget(tf_group)

        # --- Visualize ---
        viz_group = QtWidgets.QGroupBox("3. Visualize")
        viz_layout = QtWidgets.QVBoxLayout()
        self.btn_viz = QtWidgets.QPushButton("Load CSV & Plot")
        self.btn_viz.clicked.connect(self.run_visualize)
        viz_layout.addWidget(self.btn_viz)
        viz_group.setLayout(viz_layout)
        left_layout.addWidget(viz_group)

        left_layout.addStretch()

        # ===== RIGHT PANEL (VISUALIZATION / OUTPUT) =====
        right_panel = QtWidgets.QWidget()
        self.right_layout = QtWidgets.QVBoxLayout(right_panel)
        
        self.canvas = MplCanvas(self, width=10, height=8, dpi=100)
        
        # Add the Navigation Toolbar right above the canvas
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.right_layout.addWidget(self.toolbar)
        
        self.right_layout.addWidget(self.canvas)

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, stretch=1)

        # Internal Data State
        self.df = None
        self.expected_cols = [
            "time", "Bx_t","By_t","Bz_t", "Bx_m","By_m","Bz_m",
            "PWMb_x","PWMb_y","PWMb_z", "PWM_x","PWM_y","PWM_z",
            "err_x","err_y","err_z"
        ]

    # ================= UTILITIES =================
    def load_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select CSV Data Log", "", "CSV Files (*.csv)")
        if not path:
            return False

        try:
            df = pd.read_csv(path, header=None)
            
            if len(df.columns) != len(self.expected_cols):
                self.status_ind.set_color('red')
                self.status_ind.text.setText("Invalid CSV Format!")
                QtWidgets.QMessageBox.critical(self, "Error", f"Expected {len(self.expected_cols)} columns, got {len(df.columns)}.")
                return False

            df.columns = self.expected_cols
            
            # Force numeric, turn blanks into NaN
            df = df.apply(pd.to_numeric, errors='coerce')
            
            # ONLY drop the row if the 'time' column is broken/missing
            df = df.dropna(subset=["time"])
            
            # Fill the rest of the blanks with 0
            df = df.fillna(0.0)
            
            # Normalize time
            df["time"] = df["time"] - df["time"].iloc[0]
            
            self.df = df
            self.status_ind.set_color('green')
            self.status_ind.text.setText("CSV Loaded Successfully")
            return True
            
        except Exception as e:
            self.status_ind.set_color('red')
            self.status_ind.text.setText("Error reading CSV")
            print(f"Load Error: {e}")
            return False

    # ================= 1. PID AUTO TUNE =================
    def run_pid_tune(self):
        if not self.load_csv(): return

        t = self.df["time"].to_numpy()
        err_x = self.df["err_x"].to_numpy()
        err_y = self.df["err_y"].to_numpy()
        err_z = self.df["err_z"].to_numpy()

        # MATLAB logic translation
        eNorm = np.sqrt(err_x**2 + err_y**2 + err_z**2)
        eVar = np.var(eNorm)
        Tspan = t[-1] - t[0] if len(t) > 1 else 1.0
        if Tspan <= 0: Tspan = 1.0

        Kp_sug = 0.5 / max(1e-3, np.sqrt(eVar))
        Ki_sug = 0.1 / max(1e-3, Tspan)

        self.lbl_pid_out.setText(f"Suggested Kp: {Kp_sug:.4f}\nSuggested Ki: {Ki_sug:.4f}")

    # ================= 2. GENERATE TF =================
    # ================= 2. GENERATE TF =================
    def crude_first_order(self, t, target, meas):
        # 1. Find the step size and direction
        U = target[-1] - target[0] 
        if abs(U) < 1e-3: 
            return "K=0, tau=0"
        
        # 2. Find exactly WHEN the step command was sent
        step_indices = np.where(np.abs(target - target[0]) > 1e-3)[0]
        step_start_time = t[step_indices[0]] if len(step_indices) > 0 else 0.0
        
        # 3. Calculate Gain (K)
        # Use the average of the first and last 10 points to avoid noise spikes
        start_meas = np.mean(meas[:10])
        end_meas = np.mean(meas[-10:])
        yss_change = end_meas - start_meas
        
        K = yss_change / U
        
        # 4. Find Time Constant (Tau)
        # Apply a 5-point moving average to smooth out magnetometer noise
        meas_smooth = pd.Series(meas).rolling(window=5, min_periods=1).mean().to_numpy()
        
        # The target is 63.2% of the journey from the start value to the end value
        target_val = start_meas + (0.632 * yss_change)
        
        # Look for the target ONLY after the step was actually commanded
        if U > 0: # Positive step
            valid_idx = np.where((t >= step_start_time) & (meas_smooth >= target_val))[0]
        else:     # Negative step
            valid_idx = np.where((t >= step_start_time) & (meas_smooth <= target_val))[0]
            
        if len(valid_idx) > 0:
            # Tau is the time it hit 63.2% MINUS the time the command was sent
            tau = t[valid_idx[0]] - step_start_time
        else:
            tau = max(t) / 3.0
            
        if tau <= 0: 
            tau = max(t) / 3.0
            
        return f"K={K:.3f}, τ={tau:.3f}s"

    def run_generate_tf(self):
        if not self.load_csv(): return

        t = self.df["time"].to_numpy()
        gx = self.crude_first_order(t, self.df["Bx_t"].to_numpy(), self.df["Bx_m"].to_numpy())
        gy = self.crude_first_order(t, self.df["By_t"].to_numpy(), self.df["By_m"].to_numpy())
        gz = self.crude_first_order(t, self.df["Bz_t"].to_numpy(), self.df["Bz_m"].to_numpy())

        self.lbl_tf_out.setText(f"Gx: {gx}\nGy: {gy}\nGz: {gz}")

    # ================= 3. VISUALIZE =================
    def run_visualize(self):
        if not self.load_csv(): return

        # Clear existing plots
        for ax in self.canvas.axes:
            ax.clear()

        df = self.df
        
        # EXTRACT TO NUMPY ARRAYS FIRST
        t = df["time"].to_numpy()
        
        Bx_t, By_t, Bz_t = df["Bx_t"].to_numpy(), df["By_t"].to_numpy(), df["Bz_t"].to_numpy()
        Bx_m, By_m, Bz_m = df["Bx_m"].to_numpy(), df["By_m"].to_numpy(), df["Bz_m"].to_numpy()
        err_x, err_y, err_z = df["err_x"].to_numpy(), df["err_y"].to_numpy(), df["err_z"].to_numpy()
        PWM_x, PWM_y, PWM_z = df["PWM_x"].to_numpy(), df["PWM_y"].to_numpy(), df["PWM_z"].to_numpy()
        PWMb_x, PWMb_y, PWMb_z = df["PWMb_x"].to_numpy(), df["PWMb_y"].to_numpy(), df["PWMb_z"].to_numpy()

        # Plot 1: Tracking
        ax = self.canvas.axes[0]
        ax.set_title("Tracking (Target vs Meas)")
        ax.plot(t, Bx_t, 'r--', label="Bx_tgt")
        ax.plot(t, Bx_m, 'r', label="Bx_m")
        ax.plot(t, By_t, 'g--', label="By_tgt")
        ax.plot(t, By_m, 'g', label="By_m")
        ax.plot(t, Bz_t, 'b--', label="Bz_tgt")
        ax.plot(t, Bz_m, 'b', label="Bz_m")
        ax.legend(fontsize=8)
        ax.grid()

        # Plot 2: Error
        ax = self.canvas.axes[1]
        ax.set_title("Error")
        ax.plot(t, err_x, 'r', label="err_x")
        ax.plot(t, err_y, 'g', label="err_y")
        ax.plot(t, err_z, 'b', label="err_z")
        ax.legend(fontsize=8)
        ax.grid()

        # Plot 3: PWM Output
        ax = self.canvas.axes[2]
        ax.set_title("PWM Output (Total)")
        ax.plot(t, PWM_x, 'r', label="PWM_x")
        ax.plot(t, PWM_y, 'g', label="PWM_y")
        ax.plot(t, PWM_z, 'b', label="PWM_z")
        ax.legend(fontsize=8)
        ax.grid()

        # Plot 4: PWM Base vs Total PWM
        ax = self.canvas.axes[3]
        ax.set_title("PWM_base vs PWM_total")
        ax.plot(t, PWMb_x, 'r--', label="Pb_x")
        ax.plot(t, PWM_x, 'r', label="P_x")
        ax.plot(t, PWMb_y, 'g--', label="Pb_y")
        ax.plot(t, PWM_y, 'g', label="P_y")
        ax.plot(t, PWMb_z, 'b--', label="Pb_z")
        ax.plot(t, PWM_z, 'b', label="P_z")
        ax.legend(fontsize=8)
        ax.grid()

        # Plot 5: Error Magnitude
        ax = self.canvas.axes[4]
        ax.set_title("Total Error Magnitude")
        err_norm = np.sqrt(err_x**2 + err_y**2 + err_z**2)
        ax.plot(t, err_norm, 'k')
        ax.grid()

        # Draw the updated canvas
        self.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DataAnalysisTool()
    window.show()
    sys.exit(app.exec_())