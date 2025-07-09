#!/usr/bin/env python3

import argparse
import glob
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

def report_nans(mocap_dir):
    files = sorted(
        f for f in glob.glob(os.path.join(mocap_dir, '*.csv'))
        if '063025' in os.path.basename(f)
    )
    print(f"Checking {len(files)} mocap files for missing values…\n")
    for f in files:
        df = pd.read_csv(f)
        total_nans = int(df.isna().sum().sum())
        if total_nans == 0:
            print(f"{os.path.basename(f):30s}  OK — no NaNs")
        else:
            col_nans = df.isna().sum()
            print(f"{os.path.basename(f):30s}  {total_nans} total NaNs")
            for col, cnt in col_nans[col_nans > 0].items():
                print(f"    {col:20s} → {cnt}")
    print("\nDone.")


def load_data(sensor_dir, mocap_dir):
    """
    Load sensor and mocap data and treat each time-sample (row) as an example.

    Returns:
    - X: 2D array of shape (total_samples, n_sensor_features)
    - y: 2D array of shape (total_samples, n_mocap_features)
    - common_sensor_cols: list of sensor columns retained
    - common_mocap_cols: list of mocap columns retained
    """
    sensor_files = sorted(
        f for f in glob.glob(os.path.join(sensor_dir, '*sensor*.csv'))
        if '063025' in os.path.basename(f)
    )
    X_dfs, y_dfs = [], []

    for sf in sensor_files:
        bn = os.path.basename(sf)
        base = bn.replace('_sensor', '').rsplit('.csv', 1)[0]
        pattern = os.path.join(mocap_dir, f"{base}*resamp*.csv")
        matches = glob.glob(pattern)
        mf = matches[0] if matches else os.path.join(mocap_dir, bn.replace('_sensor', ''))

        if not os.path.exists(mf):
            print(f"⚠️  Missing mocap for {bn}, skipping.")
            continue

        df_X = pd.read_csv(sf).drop(columns=['Time_ms'], errors='ignore')
        df_y = pd.read_csv(mf)
        print(f"\nLoaded pair: {bn} ↔ {os.path.basename(mf)}")
        print(f"  rows: sensor={len(df_X)}, mocap={len(df_y)}")

        # assume sensor and mocap rows match; else skip
        if len(df_X) != len(df_y):
            print(f"  ⚠️  row count mismatch, skipping this pair.")
            continue

        X_dfs.append(df_X)
        y_dfs.append(df_y)

    if not X_dfs:
        raise RuntimeError("No valid sensor/mocap pairs found.")

    # Determine common columns
    common_sensor_cols = sorted(
        set.intersection(*(set(df.columns) for df in X_dfs))
    )
    common_mocap_cols = sorted(
        set.intersection(*(set(df.columns) for df in y_dfs))
    )
    print(f"Keeping {len(common_sensor_cols)} common sensor cols and {len(common_mocap_cols)} common mocap cols")

    # Concatenate rows across all trials
    X_all = pd.concat([df[common_sensor_cols] for df in X_dfs], axis=0, ignore_index=True)
    y_all = pd.concat([df[common_mocap_cols] for df in y_dfs], axis=0, ignore_index=True)

    return X_all.values, y_all.values, common_sensor_cols, common_mocap_cols


def main():
    parser = argparse.ArgumentParser(description='Train sensor-to-mocap regression model.')
    parser.add_argument('--sensor_dir', required=True, help='Directory of sensor CSV files.')
    parser.add_argument('--mocap_dir', required=True, help='Directory of cleaned mocap CSV files.')
    parser.add_argument('--output_dir', required=True, help='Directory to save model and metrics.')
    parser.add_argument('--test_size', type=float, default=0.2, help='Fraction of data for validation.')
    parser.add_argument('--random_state', type=int, default=42, help='Random seed.')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    report_nans(args.mocap_dir)
    X, y, sensor_cols, mocap_cols = load_data(args.sensor_dir, args.mocap_dir)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )
    model = MultiOutputRegressor(
        RandomForestRegressor(n_estimators=100, random_state=args.random_state)
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    mse = mean_squared_error(y_val, y_pred)
    mae = mean_absolute_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)

    metrics_path = os.path.join(args.output_dir, 'metrics.txt')
    with open(metrics_path, 'w') as f:
        f.write(f'Validation on {len(y_val)} samples:\n')
        f.write(f'MSE: {mse:.4f}\n')
        f.write(f'MAE: {mae:.4f}\n')
        f.write(f'R2: {r2:.4f}\n')
    print(f'Metrics saved to {metrics_path}')

    model_path = os.path.join(args.output_dir, 'model.joblib')
    joblib.dump({'model': model, 'sensor_columns': sensor_cols, 'mocap_columns': mocap_cols}, model_path)
    print(f'Model saved to {model_path}')

if __name__ == '__main__':
    main()
