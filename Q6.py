import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

# -----------------------------
# 0. Load Data
# -----------------------------
file_path = r"C:\Users\DELL\Desktop\SRAJAN-Multi_sensor_condition_monitoring\sensor_monitoring_analysis.xlsx"
df = pd.read_excel(file_path)

# -----------------------------
# 1. CLEAN COLUMN NAMES (ROBUST)
# -----------------------------
df.columns = (
    df.columns
    .str.strip()
    .str.replace(r'\s+', '', regex=True)   # remove ALL spaces
    .str.replace('_', '')
    .str.replace('-', '')
)

print("Cleaned Columns:")
print(df.columns.tolist())

# -----------------------------
# 2. AUTO-DETECT REQUIRED COLUMNS
# -----------------------------
column_map = {
    "temperature": None,
    "vibration": None,
    "pressure": None,
    "energyconsumption": None,
    "defectcount": None,
    "productionunits": None,
    "machineid": None
}

for col in df.columns:
    key = col.lower()
    for target in column_map:
        if target in key:
            column_map[target] = col

print("\nDetected Columns:")
print(column_map)

# Check missing
missing = [k for k, v in column_map.items() if v is None]
if missing:
    raise ValueError(f"Still missing columns: {missing}")

# Assign columns
temp_col = column_map["temperature"]
vib_col = column_map["vibration"]
pres_col = column_map["pressure"]
energy_col = column_map["energyconsumption"]
defect_col = column_map["defectcount"]
prod_col = column_map["productionunits"]
machine_col = column_map["machineid"]

features = [temp_col, vib_col, pres_col, energy_col, defect_col]

# -----------------------------
# 3. HANDLE MISSING VALUES
# -----------------------------
df[features] = df[features].fillna(df[features].mean())

# -----------------------------
# 4. BUILD HEALTH SCORE
# -----------------------------
scaler = StandardScaler()
Z = scaler.fit_transform(df[features])

Z_df = pd.DataFrame(Z, columns=[f + "_Z" for f in features])
df = pd.concat([df, Z_df], axis=1)

df["HealthScore_raw"] = (
    0.25 * abs(df[temp_col + "_Z"]) +
    0.25 * abs(df[vib_col + "_Z"]) +
    0.20 * abs(df[pres_col + "_Z"]) +
    0.20 * abs(df[energy_col + "_Z"]) +
    0.10 * abs(df[defect_col + "_Z"])
)

# Normalize safely
denominator = df["HealthScore_raw"].max() - df["HealthScore_raw"].min()

if denominator == 0:
    df["HealthScore"] = 0
else:
    df["HealthScore"] = 100 * (
        (df["HealthScore_raw"] - df["HealthScore_raw"].min()) / denominator
    )

print("\nHealthScore created successfully!")

# -----------------------------
# 5. TRAIN MODEL
# -----------------------------
X = df[[temp_col, vib_col, pres_col, energy_col, prod_col]]
y = df["HealthScore"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# -----------------------------
# 6. EVALUATE
# -----------------------------
print("\nModel Performance:")
print("R2 Score:", r2_score(y_test, y_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))

# -----------------------------
# 7. FEATURE IMPORTANCE
# -----------------------------
importances = pd.Series(
    model.feature_importances_,
    index=X.columns
).sort_values(ascending=False)

print("\nFeature Importance:")
print(importances.to_string())

print("\nTop Driver of Machine Health:", importances.index[0])

# -----------------------------
# 8. WORST MACHINES
# -----------------------------
worst = df.sort_values("HealthScore", ascending=False).head(10)

print("\nTop 10 Worst Machines:")
print(worst[[machine_col, "HealthScore"]])

# -----------------------------
# 9. SAVE RESULTS
# -----------------------------
df.to_excel("Sensor_Health_Results.xlsx", index=False)

print("\nResults saved to Sensor_Health_Results.xlsx")