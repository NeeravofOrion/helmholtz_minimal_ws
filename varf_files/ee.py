import numpy as np
import csv
import math

# ===== TRAJECTORY PARAMETERS =====
amplitude = 100.0       # Max field in µT
period = 30.0           # Seconds for one full sine wave
step_time = 0.75         # 2 seconds to allow hardware to settle
total_duration = 60.0  # Generate 3 full cycles (40s * 3)

# Output file name
filename = "sine_trajectory_2s_step.csv"

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    
    t = 0.0
    while t <= total_duration:
        # Calculate the target field for this time step
        bx = amplitude * math.sin((2 * math.pi / period) * t)
        by = amplitude * math.sin(((2 * math.pi / period) * t)+math.pi)
        bz = amplitude * math.sin((2 * math.pi / (period*2)) * t)
        
        # To defeat the ROS node's linear interpolation and force a true
        # 2-second "hold", we write the start and end of the hold window.
        
        # 1. Start of the 2-second hold window
        writer.writerow([round(t, 2), round(bx, 2), round(by, 2), round(bz, 2)])
        
        # 2. End of the 2-second hold window (just before the next jump)
        t_end_hold = t + step_time - 0.01
        writer.writerow([round(t_end_hold, 2), round(bx, 2), round(by, 2), round(bz, 2)])
        
        # Advance time by the step interval
        t += step_time

print(f"Generated {filename} successfully.")
print("Move this file to your ~/helmholtz_minimal_ws/varf_files/ directory.")
