import pandas as pd
from sklearn.ensemble import IsolationForest

df = pd.read_csv("clean_final.csv")

features = [
    "Temperature",
    "Vibration",
    "Pressure",
    "EnergyConsumption",
    "ProductionUnits"
]

X = df[features]

# Do NOT force anomaly %
model = IsolationForest(
    n_estimators=100,
    random_state=42
)

model.fit(X)

# anomaly score (lower = more abnormal)
df["anomaly_score"] = model.decision_function(X)

# Sort by severity and take worst 200
top_200 = df.sort_values("anomaly_score").head(200)

final_output = top_200[["Timestamp", "MachineID", "anomaly_score"]]

print(final_output)

final_output.to_csv("top_200_anomalies.csv", index=False)
pd.set_option('display.max_rows', 250)
print(top_200)