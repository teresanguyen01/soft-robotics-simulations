import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('data/raise_lhand_mocap_cleaned.csv')

# 2. Extract left‐side markers
L_sho = df[['left_shoulder_X', 'left_shoulder_Y', 'left_shoulder_Z']].values
L_elb = df[['left_elbow_X',    'left_elbow_Y',    'left_elbow_Z']].values
L_wra = df[['left_wrist_a_X',   'left_wrist_a_Y',   'left_wrist_a_Z']].values
L_wrb = df[['left_wrist_b_X',   'left_wrist_b_Y',   'left_wrist_b_Z']].values
L_wri = (L_wra + L_wrb) * 0.5

# 3. Extract right‐side markers
R_sho = df[['right_shoulder_X', 'right_shoulder_Y', 'right_shoulder_Z']].values
R_elb = df[['right_elbow_X',    'right_elbow_Y',    'right_elbow_Z']].values
R_wra = df[['right_wrist_a_X',   'right_wrist_a_Y',   'right_wrist_a_Z']].values
R_wrb = df[['right_wrist_b_X',   'right_wrist_b_Y',   'right_wrist_b_Z']].values
R_wri = (R_wra + R_wrb) * 0.5

# 4. Function to compute elbow flexion angle (degrees)
def compute_elbow_angle(shoulder, elbow, wrist):
    v1 = shoulder - elbow
    v2 = wrist    - elbow
    dot = np.einsum('ij,ij->i', v1, v2)
    n1  = np.linalg.norm(v1, axis=1)
    n2  = np.linalg.norm(v2, axis=1)
    cos = np.clip(dot / (n1 * n2), -1.0, 1.0)
    return np.degrees(np.arccos(cos))

# 5. Calculate left & right elbow angles in degrees
angles_L_deg = compute_elbow_angle(L_sho, L_elb, L_wri)
angles_R_deg = compute_elbow_angle(R_sho, R_elb, R_wri)

# 6. Convert angles to radians
angles_L_rad = np.deg2rad(angles_L_deg)
angles_R_rad = np.deg2rad(angles_R_deg)

# 6. Extract planar shoulder translations (meters)
shoulder_r_x = df['right_shoulder_X.1'].values / 1000
shoulder_r_y = df['right_shoulder_Y.1'].values / 1000
shoulder_l_x = df['left_shoulder_X.1'].values / 1000
shoulder_l_y = df['left_shoulder_Y.1'].values / 1000

# 7. Build output DataFrame
df_out = pd.DataFrame({
    'time_ms':               df['time_ms'],
    'elbow_left':      angles_L_rad,
    'elbow_right':     angles_R_rad,
    'shoulder1_right_0': shoulder_r_x,
    'shoulder1_right_1': shoulder_r_y,
    'shoulder1_left_0':  shoulder_l_x,
    'shoulder1_left_1':  shoulder_l_y,
})

df_out.to_csv('data/elbow_angles_rad.csv', index=False)
print("Saved angled data (in radians) to data/elbow_angles_rad.csv")

# 6. Plot
time_s = df['time_ms'].values
plt.figure(figsize=(10, 5))
plt.plot(time_s, angles_L_rad, label='Left Elbow',  linewidth=2)
plt.plot(time_s, angles_R_rad, label='Right Elbow', linewidth=2)
plt.xlabel('Time (ms)')
plt.ylabel('Elbow Flexion Angle (rad)')
plt.title('Left & Right Elbow Angle Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(time_s, shoulder_r_x, label='Left Shoulder',  linewidth=2)
plt.plot(time_s, shoulder_r_y, label='Right Shoulder', linewidth=2)
plt.xlabel('Time (ms)')
plt.ylabel('position (m)')
plt.title('Left & Right Shoulder Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()