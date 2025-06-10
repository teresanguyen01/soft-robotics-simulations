import os
os.environ['PYOPENGL_PLATFORM'] = 'glx'
import genesis as gs
import numpy as np
import pandas as pd
import time

# === Init Genesis ===
gs.init(backend=gs.gpu)
scene = gs.Scene(show_viewer=True)

robot = scene.add_entity(
    gs.morphs.MJCF(file="genesis/xml/humanoid.xml"),
    vis_mode="collision"
)
# robot.set_dynamics_enabled(True)
# plane = scene.add_entity(gs.morphs.Plane(), vis_mode="collision")
scene.build()

# === Load CSV ===
df = pd.read_csv("genesis/data/angle_array_lhand_mocap.csv")

# === DOF Names from Genesis ===
dof_names = []
for joint in robot.joints:
    start, end = joint.dof_start, joint.dof_end
    count = end - start
    if count == 1:
        dof_names.append(joint.name)
    else:
        for i in range(count):
            dof_names.append(f"{joint.name}_{i}")

joint_dof_names = [name for name in dof_names if not name.startswith("root")]
dof_idx_map = {name: i for i, name in enumerate(joint_dof_names)}
# dof_idx_map = {name: i for i, name in enumerate(dof_names)}
print(dof_idx_map)

# === Corrected CSV to DOF Mapping ===
csv_to_dof = {
    'abdomen_z': ['abdomen_z_0'],
    'abdomen_y': ['abdomen_z_1'],
    'abdomen_x': ['abdomen_x'],
    'hip_x_right': ['hip_x_right_0'],
    'hip_y_right': ['hip_x_right_1'],
    'hip_z_right': ['hip_x_right_2'],
    'hip_x_left': ['hip_x_left_0'],
    'hip_y_left': ['hip_x_left_1'],
    'hip_z_left': ['hip_x_left_2'],
    'knee_right': ['knee_right'],
    'knee_left': ['knee_left'],
    'ankle_y_right': ['ankle_y_right_0'],
    'ankle_x_right': ['ankle_y_right_1'],
    'ankle_y_left': ['ankle_y_left_0'],
    'ankle_x_left': ['ankle_y_left_1'],
    'shoulder1_right': ['shoulder1_right_0'],
    'shoulder2_right': ['shoulder1_right_1'],
    'shoulder1_left': ['shoulder1_left_0'],
    'shoulder2_left': ['shoulder1_left_1'],
    'elbow_right': ['elbow_right'],
    'elbow_left': ['elbow_left']
}
qpos = np.zeros(robot.get_qpos().shape[0])
qpos[0:3] = [0, 0, 1.3]
qpos[3:7] = [1, 0, 0, 0]
for frame_idx, row in df.iterrows():
    # qpos = np.zeros(robot.get_qpos().shape[0])
    print("qpos", qpos)
    print(len(qpos))

    # Root pose
    # qpos[0:3] = row[['x', 'y', 'z']]
    # qpos[3:7] = row[['qw', 'qx', 'qy', 'qz']]

    # DOF values
    for csv_col, dof_list in csv_to_dof.items():
        for dof in dof_list:
            if dof in dof_idx_map:
                idx = dof_idx_map[dof] + 7
                print(idx)
                qpos[idx] = row[csv_col]

    # Apply and step
    robot.set_qpos(qpos)
    scene.step()
