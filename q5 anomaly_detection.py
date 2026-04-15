# Q5: Sensor Anomaly Detection
# Works in VS Code (.py) or Jupyter (VS Code Jupyter extension)

import pandas as pd
from sklearn.ensemble import IsolationForest
from scipy.stats import zscore

# ------------------------------
# Step 1: Load your sensor data
# ------------------------------

file_path = r"C:\Users\DELL\Desktop\SRAJAN-Multi_sensor_condition_monitoring\sensor_monitoring_analysis.xlsx"
sheet_name = "Anomaly_Detail"  # change if needed
# Columns needed: Timestamp, MachineID, Temperature, Vibration, Pressure, EnergyConsumption, ProductionUnits
df = pd.read_excel(file_path, sheet_name="Anomaly_Detail")

# Keep only relevant columns
features = ['Temperature', 'Vibration', 'Pressure', 'EnergyConsumption', 'ProductionUnits']
df_features = df[features].copy()

# ------------------------------
# Step 2: Isolation Forest
# ------------------------------
iso = IsolationForest(
    n_estimators=100,
    contamination=0.05,  # adjust % of anomalies you expect
    random_state=42
)

# Fit model
df['iso_pred'] = iso.fit_predict(df_features)   # 1 = normal, -1 = anomaly
df['iso_score'] = -iso.decision_function(df_features)  # higher = more anomalous

# Top 200 anomalies by Isolation Forest
top_iso = df[df['iso_pred'] == -1].nlargest(200, 'iso_score')
top_iso_output = top_iso[['Timestamp', 'MachineID'] + features + ['iso_score']]

# Save Isolation Forest anomalies
top_iso_output.to_excel("Top200_Anomalies_ISO.xlsx", index=False)
print("Top 200 anomalies (Isolation Forest) saved to Top200_Anomalies_ISO.xlsx")

# ------------------------------
# Step 3: Z-score Anomaly Detection
# ------------------------------
df_z = df.copy()
df_z[features] = df_z[features].apply(zscore)   # normalize features

# Compute combined z-score (sum of absolute z-scores)
df_z['z_sum'] = df_z[features].abs().sum(axis=1)

# Top 200 anomalies by z-score
top_z = df_z.nlargest(200, 'z_sum')
top_z_output = top_z[['Timestamp', 'MachineID'] + features + ['z_sum']]

# Save Z-score anomalies
top_z_output.to_excel("Top200_Anomalies_ZScore.xlsx", index=False)
print("Top 200 anomalies (Z-score) saved to Top200_Anomalies_ZScore.xlsx")