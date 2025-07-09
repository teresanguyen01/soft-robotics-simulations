#!/usr/bin/env python3

import os
import argparse
from glob import glob

import pandas as pd
import numpy as np

def resample_mocap(sensor_df: pd.DataFrame, mocap_df: pd.DataFrame) -> pd.DataFrame:
    """
    Interpolate mocap data so that it matches the timestamps in the sensor data using a single concat
    to avoid repeated frame insertions and fragmentation.

    Parameters:
    - sensor_df: DataFrame containing a 'time_ms' column with sensor timestamps (normalized to start at zero).
    - mocap_df: DataFrame containing a 'time_ms' column with mocap timestamps and other columns to interpolate.

    Returns:
    - DataFrame with 'time_ms' from sensor_df and interpolated mocap columns.
    """
    # Extract timestamp arrays
    t_sensor = sensor_df['time_ms'].values
    t_mocap = mocap_df['time_ms'].values

    # Prepare base DataFrame
    resampled = pd.DataFrame({'time_ms': t_sensor})

    # Build interpolation dict for all mocap columns at once
    interp_data = {
        col: np.interp(t_sensor, t_mocap, mocap_df[col].values)
        for col in mocap_df.columns if col != 'time_ms'
    }

    # Concatenate to avoid multiple insertions
    if interp_data:
        interp_df = pd.DataFrame(interp_data)
        resampled = pd.concat([resampled, interp_df], axis=1)

    return resampled


def process_pair(sensor_file: str, mocap_file: str, output_file: str) -> None:
    """
    Read sensor and mocap CSVs, normalize sensor time to start at zero,
    resample mocap to sensor timestamps, and save output.
    """
    # Load data
    sensor_df = pd.read_csv(sensor_file)
    mocap_df = pd.read_csv(mocap_file)

    # Rename sensor column from 'Time_ms' to 'time_ms' for consistency
    if 'Time_ms' in sensor_df.columns:
        sensor_df.rename(columns={'Time_ms': 'time_ms'}, inplace=True)

    # Ensure data is sorted by time
    sensor_df = sensor_df.sort_values('time_ms')
    mocap_df = mocap_df.sort_values('time_ms')

    # Normalize sensor time to start at zero while preserving intervals
    sensor_start = sensor_df['time_ms'].iloc[0]
    sensor_df['time_ms'] = sensor_df['time_ms'] - sensor_start

    # Resample mocap data
    resampled_df = resample_mocap(sensor_df, mocap_df)
    resampled_df.to_csv(output_file, index=False)


def main(sensor_dir: str, mocap_dir: str, output_dir: str) -> None:
    """
    Find sensor files in sensor_dir, match mocap files in mocap_dir,
    resample mocap data to sensor timestamps, and write to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Look for sensor files in the sensor directory
    sensor_pattern = os.path.join(sensor_dir, '*sensor*.csv')
    sensor_files = glob(sensor_pattern)

    if not sensor_files:
        print(f"No sensor files found in {sensor_dir} matching '*sensor*.csv'.")
        return

    for sensor_path in sensor_files:
        filename = os.path.basename(sensor_path)
        # Derive corresponding mocap filename by removing the '_sensor' part
        mocap_filename = filename.replace('_sensor', '')
        mocap_path = os.path.join(mocap_dir, mocap_filename)

        if not os.path.exists(mocap_path):
            print(f"Warning: No matching mocap file for '{filename}' in mocap_dir (expected '{mocap_filename}').")
            continue

        # Construct an output filename
        name_root, _ = os.path.splitext(mocap_filename)
        output_filename = f"{name_root}_resamp.csv"
        output_path = os.path.join(output_dir, output_filename)

        process_pair(sensor_path, mocap_path, output_path)
        print(f"Resampled '{mocap_filename}' -> '{output_filename}'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Resample mocap data to match sensor timestamps using linear interpolation.'
    )
    parser.add_argument(
        '--sensor_dir', '-s', required=True,
        help='Directory containing sensor CSV files.'
    )
    parser.add_argument(
        '--mocap_dir', '-m', required=True,
        help='Directory containing mocap CSV files.'
    )
    parser.add_argument(
        '--output_dir', '-o', required=True,
        help='Directory to save the resampled mocap CSV files.'
    )
    args = parser.parse_args()

    main(args.sensor_dir, args.mocap_dir, args.output_dir)
