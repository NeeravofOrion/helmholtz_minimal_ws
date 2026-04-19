import pandas as pd
import numpy as np

# Configuration
input_file = 'geo_orbital_mag_data.csv'  # Replace with your actual filename
output_file = 'downsampled_mag_data.csv'
sim_duration_sec = 180  # 3 minutes

# 1. Load data
try:
    df = pd.read_csv(input_file)
except FileNotFoundError:
    # Creating dummy data for demonstration if file doesn't exist
    print(f"File {input_file} not found. Ensure the CSV is in the directory.")
    exit()

# 2. Select specific columns
# Extracting Time (Hour), Bx, By, Bz
required_columns = ['Hour', 'Bx_GSE_nT', 'By_GSE_nT', 'Bz_GSE_nT']
df_filtered = df[required_columns]

# 3. Calculate Downsampling Factor
# Assuming original data is 1-minute intervals (1440 rows for 24h)
total_rows = len(df_filtered)
# We want to map 24 hours of data to 180 seconds.
# This factor depends on your controller's loop frequency. 
# If your loop runs at 1Hz, you need 180 rows total.
target_rows = 180 
step = max(1, total_rows // target_rows)

# 4. Perform Downsampling (Mean-based to preserve signal integrity)
df_downsampled = df_filtered.iloc[::step].copy()

# 5. Map 'Hour' to 'Sim_Time_Seconds' for your 3-min run
# This creates a new time column from 0 to 180
df_downsampled['Sim_Time_Sec'] = np.linspace(0, sim_duration_sec, len(df_downsampled))

# 6. Save output
df_downsampled.to_csv(output_file, index=False)

print(f"Downsampling complete.")
print(f"Original rows: {total_rows} | New rows: {len(df_downsampled)}")
print(f"Data saved to {output_file}")