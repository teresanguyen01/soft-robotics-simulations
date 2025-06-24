import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
from sklearn.decomposition import PCA

# 1. Load raw data
df_sensors = pd.read_csv('sensor_data/rhand_sensor.csv')  # columns: Time (ms), Sensor 1…Sensor 24
df_mocap   = pd.read_csv('data/aa_rhand_new.csv')         # columns: time_ms, root_x, root_y, root_z, root_qw, root_qx, root_qy, root_qz,
                                                           #           abdomen_z_0, abdomen_z_1,
                                                           #           shoulder1_right_0, shoulder1_right_1,
                                                           #           shoulder1_left_0, shoulder1_left_1,
                                                           #           abdomen_x, elbow_right, elbow_left,
                                                           #           … (other lower‐body joints) …

# 2. Ensure timestamp types match
df_sensors["Time (ms)"] = df_sensors["Time (ms)"].astype(float)
df_mocap["time_ms"]     = df_mocap["time_ms"].astype(float)

# 3. Time‐synchronized merge (nearest neighbor)
df_all = pd.merge_asof(
    df_sensors.sort_values("Time (ms)"),
    df_mocap.sort_values("time_ms"),
    left_on="Time (ms)",
    right_on="time_ms",
    direction="nearest"
)

# 4. Static calibration (remove per‐sensor DC offset)
sensor_cols = [f"Sensor {i}" for i in range(1, 25)]
rest_means = df_all.iloc[:100][sensor_cols].mean()   # assume first 100 samples = rest
df_cal = df_all.copy()
for c in sensor_cols:
    df_cal[c] -= rest_means[c]

# 5. Drift removal: high‐pass filter (0.1 Hz cutoff)
fs    = 100.0   # sampling rate [Hz]
fc_hp = 0.1     # high‐pass cutoff [Hz]
b_hp, a_hp = butter(4, fc_hp/(fs/2), btype='high')
for c in sensor_cols:
    df_cal[c] = filtfilt(b_hp, a_hp, df_cal[c])

# 6. Noise reduction: low‐pass filter (12 Hz cutoff)
fc_lp = 12.0    # low‐pass cutoff [Hz]
b_lp, a_lp = butter(4, fc_lp/(fs/2), btype='low')
df_filt = df_cal.copy()
for c in sensor_cols:
    df_filt[c] = filtfilt(b_lp, a_lp, df_cal[c])

# 7. Outlier clipping & interpolation
df_clipped = df_filt.copy()
for c in sensor_cols:
    mu, sigma = df_filt[c].mean(), df_filt[c].std()
    mask = (df_filt[c] - mu).abs() > 3*sigma
    df_clipped.loc[mask, c] = np.nan
    df_clipped[c].interpolate(method='linear', limit=5, inplace=True)

# 8. Normalization (zero‐mean, unit‐variance)
df_norm = df_clipped.copy()
for c in sensor_cols:
    mu, sigma = df_clipped[c].mean(), df_clipped[c].std()
    df_norm[c] = (df_clipped[c] - mu) / sigma

# 9. Select only upper‐body joints as targets
upper_body = [
    'x','y','z','qw','qx','qy','qz',
    'abdomen_z_0','abdomen_z_1',
    'shoulder1_right_0','shoulder1_right_1',
    'shoulder1_left_0','shoulder1_left_1',
    'abdomen_x','elbow_right','elbow_left'
]
joint_cols = [c for c in df_all.columns if c in upper_body]

# 10. Correlate sensors to each joint & group
corr = df_norm[sensor_cols + joint_cols].corr().loc[sensor_cols, joint_cols]
threshold = 0.4
sensor_groups = {
    joint: corr[joint].abs().loc[lambda x: x >= threshold].index.tolist()
    for joint in joint_cols
}

# 11. Feature engineering
df_feat = df_norm.copy()

# 11a. Velocity (first‐difference)
for c in sensor_cols:
    df_feat[f"{c}_vel"] = df_feat[c].diff().fillna(0)

# 11b. Rolling mean (window = 5 samples)
for c in sensor_cols:
    df_feat[f"{c}_roll"] = df_feat[c].rolling(window=5, min_periods=1).mean()

# 11c. Group summaries: mean + PCA‐1
for joint, grp in sensor_groups.items():
    if grp:
        df_feat[f"{joint}_mean"] = df_feat[grp].mean(axis=1)
        pca = PCA(n_components=1)
        df_feat[f"{joint}_pc1"]  = pca.fit_transform(df_feat[grp])

# 12. Assemble final dataset
feature_cols = [
    c for c in df_feat.columns
    if c in sensor_cols
       or c.endswith('_vel')
       or c.endswith('_roll')
       or c.endswith('_mean')
       or c.endswith('_pc1')
]

final_df = df_feat[['time_ms'] + feature_cols + joint_cols]

# 13. Save for ML training
final_df.to_csv('sensor_angles_features.csv', index=False)
