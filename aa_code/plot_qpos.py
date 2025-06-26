#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(
        description="Plot joint angles (radians) and translations (meters) over time from a CSV."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input CSV file (e.g. angle_arrays/Apose_062325.csv)"
    )
    args = parser.parse_args()

    # 1) load the CSV via CLI
    df = pd.read_csv(args.input)

    # 2) specify which channels are angles vs. translations
    radian_channels = [
        "abdomen_x", "abdomen_z_0", "abdomen_z_1",
        "elbow_right", "elbow_left",
        "hip_x_right_0", "hip_x_right_1", "hip_x_right_2",
        "hip_x_left_0",  "hip_x_left_1",  "hip_x_left_2",
        "shoulder1_right_0", "shoulder1_right_1",
        "shoulder1_left_0",  "shoulder1_left_1",
        "knee_right",    "knee_left",
    ]

    linear_channels = [
        "x", "y", "z"               # root
        # "abdomen_z_0", "abdomen_z_1",     # abdomen plane
        # "ankle_y_right_0",   "ankle_y_right_1",
        # "ankle_y_left_0",    "ankle_y_left_1",
    ]

    # 3a) plot all the radians on one figure
    plt.figure()
    cmap = plt.get_cmap('tab20')
    num_rad = len(radian_channels)
    for idx, name in enumerate(radian_channels):
        if name in df:
            color = cmap(idx / num_rad)
            plt.plot(df["time_ms"], df[name], label=name, color=color)
    plt.title("Joint Angles (radians) over Time")
    plt.xlabel("time (ms)")
    plt.ylabel("angle (rad)")
    plt.legend(loc="upper right", fontsize="small")
    plt.tight_layout()

    # 3b) plot all the linear translations on another
    plt.figure()
    for name in linear_channels:
        if name in df:
            plt.plot(df["time_ms"], df[name], label=name)
    plt.title("Joint Translations (meters) over Time")
    plt.xlabel("time (ms)")
    plt.ylabel("distance (m)")
    plt.legend(loc="upper right", fontsize="small")
    plt.tight_layout()

    # 4) show both plots
    plt.show()

if __name__ == "__main__":
    main()
