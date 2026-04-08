import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# ===== INPUT FROM TERMINAL =====
if len(sys.argv) < 2:
    print("Usage: python3 analyze.py <filename.csv>")
    sys.exit(1)

filename = sys.argv[1]

# ===== RESOLVE PATH =====
# assumes script and CSV are in same folder
file = os.path.join(os.getcwd(), filename)

if not os.path.exists(file):
    print(f"File not found: {file}")
    sys.exit(1)

print(f"Using file: {file}")

# ===== LOAD FILE =====
df = pd.read_csv(file, header=None)

# ===== ASSIGN COLUMNS =====
df.columns = [
    "time",
    "Bx_t","By_t","Bz_t",
    "Bx_m","By_m","Bz_m",
    "PWMb_x","PWMb_y","PWMb_z",
    "PWM_x","PWM_y","PWM_z",
    "err_x","err_y","err_z"
]

# ===== FORCE NUMERIC =====
df = df.apply(pd.to_numeric, errors='coerce')
df = df.dropna()

# ===== TIME =====
t = (df["time"] - df["time"].iloc[0]).to_numpy()

# ===== EXTRACT =====
Bx_t = df["Bx_t"].to_numpy()
By_t = df["By_t"].to_numpy()
Bz_t = df["Bz_t"].to_numpy()

Bx_m = df["Bx_m"].to_numpy()
By_m = df["By_m"].to_numpy()
Bz_m = df["Bz_m"].to_numpy()

err_x = df["err_x"].to_numpy()
err_y = df["err_y"].to_numpy()
err_z = df["err_z"].to_numpy()

PWM_x = df["PWM_x"].to_numpy()
PWM_y = df["PWM_y"].to_numpy()
PWM_z = df["PWM_z"].to_numpy()

PWMb_x = df["PWMb_x"].to_numpy()
PWMb_y = df["PWMb_y"].to_numpy()
PWMb_z = df["PWMb_z"].to_numpy()

# ===== METRICS =====
def compute_metrics(target, meas):
    steady_state_error = abs(target[-1] - meas[-1])
    peak_error = np.max(np.abs(target - meas))

    final = target[-1]

    try:
        idx_10 = np.where(meas >= 0.1 * final)[0][0]
        idx_90 = np.where(meas >= 0.9 * final)[0][0]
        rise_time = t[idx_90] - t[idx_10]
    except:
        rise_time = np.nan

    return steady_state_error, peak_error, rise_time


print("\n===== SYSTEM METRICS =====")
for axis, tgt, meas in zip(
    ["X","Y","Z"],
    [Bx_t, By_t, Bz_t],
    [Bx_m, By_m, Bz_m]
):
    ss, peak, rise = compute_metrics(tgt, meas)
    print(f"{axis}: SS_err={ss:.2f}, Peak_err={peak:.2f}, Rise={rise:.2f}s")


# ===== PLOTS =====
plt.figure()
plt.title("Tracking")
plt.plot(t, Bx_t, linestyle='--', label="Bx_target")
plt.plot(t, Bx_m, label="Bx_meas")
plt.plot(t, By_t, linestyle='--', label="By_target")
plt.plot(t, By_m, label="By_meas")
plt.plot(t, Bz_t, linestyle='--', label="Bz_target")
plt.plot(t, Bz_m, label="Bz_meas")
plt.legend()
plt.grid()

plt.figure()
plt.title("Error")
plt.plot(t, err_x, label="err_x")
plt.plot(t, err_y, label="err_y")
plt.plot(t, err_z, label="err_z")
plt.legend()
plt.grid()

plt.figure()
plt.title("PWM Output")
plt.plot(t, PWM_x, label="PWM_x")
plt.plot(t, PWM_y, label="PWM_y")
plt.plot(t, PWM_z, label="PWM_z")
plt.legend()
plt.grid()

plt.figure()
plt.title("PWM_base vs PWM")
plt.plot(t, PWMb_x, linestyle='--', label="PWMb_x")
plt.plot(t, PWM_x, label="PWM_x")
plt.plot(t, PWMb_y, linestyle='--', label="PWMb_y")
plt.plot(t, PWM_y, label="PWM_y")
plt.plot(t, PWMb_z, linestyle='--', label="PWMb_z")
plt.plot(t, PWM_z, label="PWM_z")
plt.legend()
plt.grid()

plt.figure()
plt.title("Error Magnitude")
err_norm = np.sqrt(err_x**2 + err_y**2 + err_z**2)
plt.plot(t, err_norm)
plt.grid()

plt.show()