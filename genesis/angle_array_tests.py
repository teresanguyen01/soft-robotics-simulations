import os
os.environ['PYOPENGL_PLATFORM'] = 'glx'
import genesis as gs
import numpy as np
import pandas as pd
import time


gs.init(backend=gs.gpu)

scene = gs.Scene(show_viewer=True)

robot = scene.add_entity(
    gs.morphs.MJCF(file="genesis/xml/humanoid.xml"),
    vis_mode="collision"
)
print("joints", robot.joints)
plane = scene.add_entity(gs.morphs.Plane(), vis_mode="collision")
scene.build()
df = pd.read_csv("genesis/data/angle_array_double_arm_lat.csv")

# dof_names = [joint.name for joint in robot.joints]

csv_to_dof = {
    'abdomen_z': ['abdomen_z_0', 'abdomen_z_1'],
    'shoulder1_right': ['shoulder1_right_0'],
    'shoulder2_right': ['shoulder1_right_1'],
    'shoulder1_left': ['shoulder1_left_0'],
    'shoulder2_left': ['shoulder1_left_1'],
    'abdomen_x': ['abdomen_x'],
    'elbow_right': ['elbow_right'],
    'elbow_left': ['elbow_left'],
    'hip_x_right': ['hip_x_right_0'],
    'hip_y_right': ['hip_x_right_1'],
    'hip_z_right': ['hip_x_right_2'],
    'hip_x_left': ['hip_x_left_0'],
    'hip_y_left': ['hip_x_left_1'],
    'hip_z_left': ['hip_x_left_2'],
    'knee_right': ['knee_right'],
    'ankle_y_right': ['ankle_y_right'],
    'ankle_x_right': ['ankle_x_right'],
    'knee_left': ['knee_left'],
    'ankle_y_left': ['ankle_y_left'],
    'ankle_x_left': ['ankle_x_left']
}
# Map DOF names to indices
dof_names = []
for joint in robot.joints:
    start, end = joint.dof_start, joint.dof_end
    dof_count = end - start
    if dof_count == 1:
        dof_names.append(joint.name)
    else:
        for i in range(dof_count):
            dof_names.append(f"{joint.name}_{i}")

print("DOF Names in Genesis Order:")
for i, name in enumerate(dof_names):
    print(f"  {i + 7}: {name}")  # +7 because root takes first 7 slots

# Create mapping for easy lookup
dof_idx_map = {name: i for i, name in enumerate(dof_names)}
print("\nDOF Index Map:")
print(dof_idx_map)

print(f"robot.get_qpos().shape[0] = {robot.get_qpos().shape[0]}")
print(f"# of DOFs (excluding root): {robot.get_qpos().shape[0] - 7}")
print(f"# of joint DOFs in dof_names: {len(dof_names)}")

# Animate
for frame_idx, row in df.iterrows():
    qpos = np.zeros(robot.get_qpos().shape[0])

    # Root position and orientation
    qpos[0:3] = row[['x', 'y', 'z']]
    qpos[3:7] = row[['qw', 'qx', 'qy', 'qz']]

    print(f"\n--- Frame {frame_idx} ---")
    print(f"Root position: {qpos[0:3]}")
    print(f"Root orientation: {qpos[3:7]}")

    # Fill in joint DOFs
    for col, dofs in csv_to_dof.items():
        for i, dof in enumerate(dofs):
            if dof in dof_idx_map:
                idx = dof_idx_map[dof] + 7  # offset root DOFs
                value = row[col]
                if idx >= len(qpos):
                    print(f"[ERROR] Attempting to write qpos[{idx}], but qpos length is {len(qpos)}")
                else:
                    qpos[idx] = value
                print(f"Set qpos[{idx}] ({dof}) = {value}")
            else:
                print(f"[Warning] DOF '{dof}' from column '{col}' not found in Genesis model")

    # Pad hand joints if needed
    for name in ['hand_right_joint', 'hand_left_joint']:
        if name in dof_idx_map:
            idx = dof_idx_map[name] + 7
            qpos[idx] = 0.0
            print(f"Pad qpos[{idx}] ({name}) = 0.0")

    # Check bounds
    if np.any(np.isnan(qpos)) or np.any(np.isinf(qpos)):
        print("[Error] qpos has invalid values")
        break
    if len(qpos) != robot.get_qpos().shape[0]:
        print(f"[Error] qpos size mismatch: expected {robot.get_qpos().shape[0]}, got {len(qpos)}")
        break

    # Apply pose
    robot.set_qpos(qpos)
    scene.step()
    time.sleep(0.033)

# df = pd.read_csv("genesis/data/angle_array_lhand_mocap.csv")

# df = pd.read_csv("genesis/assets/angle_arrays/angle_array_rhand_mocap.csv")
# joint_scale = 20

# joint_order = [
#     "abdomen_z", "abdomen_y", "abdomen_x",
#     "hip_x_right", "hip_z_right", "hip_y_right",
#     "knee_right", "ankle_y_right", "ankle_x_right",
#     "hip_x_left", "hip_z_left", "hip_y_left",
#     "knee_left", "ankle_y_left", "ankle_x_left",
#     "shoulder1_right", "shoulder2_right", "elbow_right",
#     "shoulder1_left", "shoulder2_left", "elbow_left"
# ]
 
# squat_arr = [
#     0, 0, 0.596,
#     0.988015, 0, 0.154359, 0,
#     0, 0.4, 0,
#     -0.25, -0.5, -2.5, -2.65, -0.8, 0.56,
#     -0.25, -0.5, -2.5, -2.65, -0.8, 0.56,
#     0, 0, 0, 0, 0, 0
# ]
# robot.set_qpos(squat_arr)
# joint_names = robot.joints
# # print("Joint names", joint_names)
# for joint in joint_names: 
#     print(joint.name)
# for i in range(1000): 
#     scene.step()
#     time.sleep(0.2)
# print(robot.get_qpos([26]))
# print(robot.idx)
# print(abdomen_z)
# for _, row in df.iterrows(): 
#     abdomen_z.set_pos(row["abdomen_z"].to_numpy(dtype=np.float32))
#     scene.visualizer.update()

# for _, row in df.iterrows():
#     base_pos = row[["x", "y", "z"]].to_numpy(dtype=np.float32)
#     base_pos = np.array([0, 0, 1.0], dtype=np.float32)
#     base_quat = row[["qw", "qx", "qy", "qz"]].to_numpy(dtype=np.float32)

#     joint_angles = row[joint_order].to_numpy(dtype=np.float32)
#     joint_angles_scaled = joint_angles * joint_scale
#     # print(joint_angles_scaled)  
#     qpos = np.concatenate([base_pos, base_quat, joint_angles_scaled])
#     print(robot.get_joint('head_joint').link.name)
#     # print(robot.joints)
#     # print(qpos)
#     # print("DOF robot", robot.joints)
#     # print("Number of DOFs", robot.n_dofs)
#     # print("Joint angle vector shape", joint_angles.shape)
#     # print(robot)
#     robot.set_qpos(qpos)
#     # robot.set_dofs_position(joint_angles)
#     # print(dir(robot))


#     scene.visualizer.update()
#     # print(robot.get_qpos())
