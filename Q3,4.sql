use sensor_db;
SHOW TABLES;
DESCRIBE multi_sensor_anomaly;
WITH stats AS (
    SELECT
        Plant,
        AVG(Temperature) AS temp_mean,
        STDDEV(Temperature) AS temp_std,
        AVG(Vibration) AS vib_mean,
        STDDEV(Vibration) AS vib_std,
        AVG(Pressure) AS pres_mean,
        STDDEV(Pressure) AS pres_std
    FROM multi_sensor_anomaly
    GROUP BY Plant
),

anomaly_rows AS (
    SELECT
        m.Plant,
        m.MachineID
    FROM multi_sensor_anomaly m
    JOIN stats s
        ON m.Plant = s.Plant
    WHERE
        m.Temperature < s.temp_mean - 3*s.temp_std
        OR m.Temperature > s.temp_mean + 3*s.temp_std
        OR m.Vibration < s.vib_mean - 3*s.vib_std
        OR m.Vibration > s.vib_mean + 3*s.vib_std
        OR m.Pressure < s.pres_mean - 3*s.pres_std
        OR m.Pressure > s.pres_mean + 3*s.pres_std
)

SELECT
    Plant,
    MachineID,
    COUNT(*) AS AnomalyCount
FROM anomaly_rows
GROUP BY Plant, MachineID
ORDER BY AnomalyCount DESC;


--Q4--
CREATE VIEW sensor_condition_2025 AS
WITH machine_stats AS (
    SELECT
        MachineID,
        AVG(Temperature) AS AvgTemp,
        AVG(Vibration) AS AvgVib,
        AVG(Pressure) AS AvgPressure,
        AVG(EnergyConsumption / ProductionUnits) AS AvgEnergyPerUnit,
        SUM(DefectCount) AS TotalDefects,
        SUM(MaintenanceFlag) AS MaintenanceCount
    FROM multi_sensor_anomaly
    GROUP BY MachineID
),

scored AS (
    SELECT
        *,
        (AvgTemp + AvgVib + AvgPressure + TotalDefects) AS ConditionScore
    FROM machine_stats
)

SELECT
    MachineID,
    AvgTemp,
    AvgVib,
    AvgPressure,
    AvgEnergyPerUnit,
    TotalDefects,
    MaintenanceCount,
    CASE
        WHEN NTILE(10) OVER (ORDER BY ConditionScore DESC) = 1
        THEN 'Critical'
        ELSE 'Normal'
    END AS ConditionBucket
FROM scored;
SELECT * FROM sensor_condition_2025;
SHOW FULL TABLES WHERE Table_type = 'VIEW';