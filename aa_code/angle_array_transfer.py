import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load your cleaned mocap data
df = pd.read_csv('data/raise_lhand_mocap_cleaned.csv')

# 2. Extract left‐side markers
L_sho = df[['left_shoulder_X', 'left_shoulder_Y', 'left_shoulder_Z']].values
L_elb = df[['left_elbow_X',    'left_elbow_Y',    'left_elbow_Z']].values
L_wra = df[['left_wrist_a_X',   'left_wrist_a_Y',   'left_wrist_a_Z']].values
L_wrb = df[['left_wrist_b_X',   'left_wrist_b_Y',   'left_wrist_b_Z']].values
L_wri = 0.5 * (L_wra + L_wrb)    # wrist center

# 3. Extract right‐side markers
R_sho = df[['right_shoulder_X','right_shoulder_Y','right_shoulder_Z']].values
R_elb = df[['right_elbow_X',   'right_elbow_Y',   'right_elbow_Z']].values
R_wra = df[['right_wrist_a_X',  'right_wrist_a_Y',  'right_wrist_a_Z']].values
R_wrb = df[['right_wrist_b_X',  'right_wrist_b_Y',  'right_wrist_b_Z']].values
R_wri = 0.5 * (R_wra + R_wrb)

# 4. Estimate the hinge‐axis for each elbow (from frame 0)
#    by taking the cross‐product of v1 and v2 at the first frame
v1_L0 = L_sho[0] - L_elb[0]
v2_L0 = L_wri[0] - L_elb[0]
axis_L = np.cross(v1_L0, v2_L0)
axis_L = axis_L / np.linalg.norm(axis_L)

v1_R0 = R_sho[0] - R_elb[0]
v2_R0 = R_wri[0] - R_elb[0]
axis_R = np.cross(v1_R0, v2_R0)
axis_R = axis_R / np.linalg.norm(axis_R)

# 5. Signed‐angle function (radians)
def signed_elbow_angle(shoulder, elbow, wrist, hinge_axis):
    v1 = shoulder - elbow    # (N×3)
    v2 = wrist    - elbow    # (N×3)

    dot       = np.einsum('ij,ij->i', v1, v2)          # (N,)
    cross_vec = np.cross(v1, v2)                      # (N,3)
    cross_mag = np.linalg.norm(cross_vec, axis=1)     # (N,)

    # project cross_vec onto hinge_axis to get sign
    sign = np.sign(cross_vec.dot(hinge_axis))         # (N,)

    return np.arctan2(sign * cross_mag, dot)          # signed in [-π, +π]

# 6. Compute raw signed angles
raw_L = signed_elbow_angle(L_sho, L_elb, L_wri, axis_L)  # (N,)
raw_R = signed_elbow_angle(R_sho, R_elb, R_wri, axis_R)

# 7. Zero‐baseline so “straight” at frame 0 → 0 rad
elbow_left  = raw_L - raw_L[0]
elbow_right = raw_R - raw_R[0]

# 8. If you still need shoulder *planar* translations for a planar joint:
chest_x = df['chest_X.1'].values
chest_y = df['chest_Y.1'].values

shoulder_l_x = (df['left_shoulder_X.1'].values  - chest_x) / 1000  # m
shoulder_l_y = (df['left_shoulder_Y.1'].values  - chest_y) / 1000
shoulder_r_x = (df['right_shoulder_X.1'].values - chest_x) / 1000
shoulder_r_y = (df['right_shoulder_Y.1'].values - chest_y) / 1000

# 9. Build output DataFrame matching your XML DOFs
out = pd.DataFrame({
    'time_ms':            df['time_ms'],
    'shoulder1_left_0':   shoulder_l_x,
    'shoulder1_left_1':   shoulder_l_y,
    'elbow_left':         elbow_left,
    'shoulder1_right_0':  shoulder_r_x,
    'shoulder1_right_1':  shoulder_r_y,
    'elbow_right':        elbow_right,
})

out.to_csv('data/elbow_angles_rad.csv', index=False)
print("✔ Saved elbow_angles_rad.csv")

# 10. Quick sanity plots
t = df['time_ms']
plt.figure()
plt.plot(t, elbow_left,  label='L elbow')
plt.plot(t, elbow_right, label='R elbow')
plt.xlabel('Time (ms)')
plt.ylabel('Elbow flexion (rad)')
plt.legend()
plt.title('Signed, zero‐baseline elbow flexion')

plt.figure()
plt.plot(t, shoulder_l_x, label='L shoulder X (m)')
plt.plot(t, shoulder_l_y, label='L shoulder Y (m)')
plt.plot(t, shoulder_r_x, label='R shoulder X (m)')
plt.plot(t, shoulder_r_y, label='R shoulder Y (m)')
plt.xlabel('Time (ms)')
plt.ylabel('Shoulder planar pos (m)')
plt.legend()
plt.title('Shoulder planar translations')

plt.tight_layout()
plt.show()
