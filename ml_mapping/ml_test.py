#!/usr/bin/env python3
"""
predict_upper_body_angles_with_time.py

Loads the trained model and imputed features, predicts the 16-dim
upper-body angle array, reconstructs a proper time axis starting at 0,
and writes out a CSV with [time_ms, root_x, …, elbow_left].
"""

import pandas as pd
import joblib
import numpy as np
import sys

def main():
    # 1) File paths
    FEATURE_CSV = 'sensor_angles_features_imputed.csv'
    MODEL_FILE  = 'upper_body_angle_model.pkl'
    OUTPUT_CSV  = 'predicted_upper_body_angles.csv'

    # 2) Target joints
    upper_body = [
        'x','y','z','qw','qx','qy','qz',
        'abdomen_z_0','abdomen_z_1',
        'shoulder1_right_0','shoulder1_right_1',
        'shoulder1_left_0','shoulder1_left_1',
        'abdomen_x','elbow_right','elbow_left'
    ]

    # 3) Load features and model
    df = pd.read_csv(FEATURE_CSV)
    try:
        model = joblib.load(MODEL_FILE)
    except FileNotFoundError:
        print(f"Error: cannot find model file '{MODEL_FILE}'", file=sys.stderr)
        sys.exit(1)

    # 4) Reconstruct feature list by exclusion
    non_features = set(upper_body)
    # also drop any existing time columns if present
    for col in ['time_ms','Time (ms)']:
        if col in df.columns:
            non_features.add(col)
    feature_cols = [c for c in df.columns if c not in non_features]

    # 5) Sanity-check feature count
    expected = getattr(model, 'n_features_in_', model.coefs_[0].shape[0])
    if len(feature_cols) != expected:
        print(f"❌ Feature mismatch: model expects {expected} but found {len(feature_cols)}", file=sys.stderr)
        sys.exit(1)

    # 6) Predict
    X = df[feature_cols].values
    y = model.predict(X)  # shape = (n_samples, 16)

    # 7) Reconstruct time axis
    n = len(df)
    # Attempt to infer timestep from original time_ms if it's not constant
    if 'time_ms' in df.columns:
        deltas = df['time_ms'].diff().dropna().values
        dt = np.median(deltas) if np.any(deltas > 0) else 1000.0/100.0
    else:
        # default to 100 Hz sensors => 10 ms steps
        dt = 1000.0 / 100.0
    time_ms = np.arange(n) * dt

    # 8) Build output DataFrame
    df_out = pd.DataFrame(y, columns=upper_body)
    df_out.insert(0, 'time_ms', time_ms)

    # 9) Save
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Saved {n} frames to '{OUTPUT_CSV}' with time_ms from 0 to {time_ms[-1]:.1f} ms.")

if __name__ == "__main__":
    main()
