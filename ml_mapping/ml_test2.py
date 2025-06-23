import pandas as pd
import numpy as np
import joblib

MODEL_PATH   = "upper_body_angle_model.pkl"
SENSOR_PATH  = "sensor_data/rhand_sensor.csv"
ANGLE_PATH   = "data/aa_rhand_new.csv"
OUTPUT_CSV   = "data/generated_data.csv"

S_cols = [f"Sensor {i}" for i in range(1,25)]
UPPER_BODY_ANGLE_COLS = [
    'x','y','z','qw','qx','qy','qz',
    'abdomen_z_0','abdomen_z_1',
    'shoulder1_right_0','shoulder1_right_1',
    'shoulder1_left_0','shoulder1_left_1',
    'abdomen_x','elbow_right','elbow_left'
]

def main():
    df_s = pd.read_csv(SENSOR_PATH)
    if 'time_ms' not in df_s.columns:
        raise KeyError("Expected a 'time_ms' column in your sensor CSV")
    t_raw = df_s['time_ms'].values
    t0 = t_raw[0]
    t_sensor = (t_raw - t0).astype(float) 

    X = df_s[S_cols].values

    model = joblib.load(MODEL_PATH)
    Y_hat = model.predict(X)
    n_hat = Y_hat.shape[0]

    df_a = pd.read_csv(ANGLE_PATH)
    if 'time_ms' not in df_a.columns:
        raise KeyError("Expected a 'time_ms' column in your angle CSV")
    t_angle = (df_a['time_ms'].round().astype(int)).values

    if len(t_angle) != n_hat:
        Y_resampled = np.zeros((len(t_angle), Y_hat.shape[1]))
        sort_idx = np.argsort(t_sensor)
        t_sensor_sorted = t_sensor[sort_idx]
        Y_sorted       = Y_hat[sort_idx]
        for j in range(Y_hat.shape[1]):
            Y_resampled[:, j] = np.interp(t_angle, t_sensor_sorted, Y_sorted[:, j])
        Y_hat = Y_resampled
        t_out = t_angle
    else:
        t_out = t_angle

    df_out = pd.DataFrame(Y_hat, columns=UPPER_BODY_ANGLE_COLS)
    df_out.insert(0, "time_ms", t_out)

    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"→ Saved generated data ({len(df_out)} rows) to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
