import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

SENSOR_PATH = "sensor_data/rhand_sensor.csv"
ANGLE_PATH = "data/aa_rhand_new.csv"
MODEL_PATH = "upper_body_angle_model.pkl"

S_cols = [f"Sensor {i}" for i in range(1,25)]

UPPER_BODY_ANGLE_COLS = [
    'x','y','z','qw','qx','qy','qz',
    'abdomen_z_0','abdomen_z_1',
    'shoulder1_right_0','shoulder1_right_1',
    'shoulder1_left_0','shoulder1_left_1',
    'abdomen_x','elbow_right','elbow_left'
]

def load_data(sensor_path=SENSOR_PATH, angle_path=ANGLE_PATH):
    df_s = pd.read_csv(sensor_path)
    df_a = pd.read_csv(angle_path)
    t0 = df_s['time_ms'].iloc[0]
    df_s['time_ms'] = df_s['time_ms'] - t0
    df_s['time_ms'] = df_s['time_ms'].round().astype(int)
    df_a['time_ms'] = df_a['time_ms'].round().astype(int)
    df = pd.merge(df_s, df_a, on="time_ms", how="inner")
    if df.empty:
        raise RuntimeError(
            "After aligning on time_ms, the merged DataFrame is empty. "
            "Check that both files share the same timestamps."
        )
    X = df[S_cols].values
    Y = df[UPPER_BODY_ANGLE_COLS].values
    return train_test_split(X, Y, test_size=0.2, random_state=42)

if __name__ == "__main__":
    X_train, X_test, Y_train, Y_test = load_data()
    model = MLPRegressor(
        hidden_layer_sizes=(100,50),
        activation="relu",
        max_iter=500,
        random_state=42
    )
    model.fit(X_train, Y_train)
    Y_pred = model.predict(X_test)
    mse = mean_squared_error(Y_test, Y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(Y_test, Y_pred)
    print(f"Test RMSE = {rmse:.4f}, R² = {r2:.4f}")
    joblib.dump(model, MODEL_PATH)
    print(f"→ Model saved to {MODEL_PATH}")
