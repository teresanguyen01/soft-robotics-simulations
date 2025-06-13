import os
os.environ['PYOPENGL_PLATFORM'] = 'glx'
import genesis as gs
import numpy as np
import pandas as pd
import time


def print_qpos_mapping(robot):
    qpos_idx = 7  # start after root (0–6)
    print("Index | DOF Name")
    print("----------------")
    for joint in robot.joints:
        if joint.name == "root":
            continue  # skip root
        dof_count = joint.dof_end - joint.dof_start
        for i in range(dof_count):
            dof_name = f"{joint.name}_{i}" if dof_count > 1 else joint.name
            print(f"{qpos_idx:5d} | {dof_name}")
            qpos_idx += 1

gs.init(backend=gs.gpu)
scene = gs.Scene(
    show_viewer    = True,
    viewer_options = gs.options.ViewerOptions(
        res           = (1280, 960),
        camera_pos    = (3.5, 0.0, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 60,
    ),
    vis_options = gs.options.VisOptions(
        show_world_frame = True, # visualize the coordinate frame of `world` at its origin
        world_frame_size = 1.0, # length of the world frame in meter
        show_link_frame  = False, # do not visualize coordinate frames of entity links
        show_cameras     = False, # do not visualize mesh and frustum of the cameras added
        plane_reflection = True, # turn on plane reflection
        ambient_light    = (0.1, 0.1, 0.1), # ambient light setting
    ),
    renderer = gs.renderers.Rasterizer(), # using rasterizer for camera rendering
)

robot = scene.add_entity(
    gs.morphs.MJCF(file="genesis/xml/humanoid.xml"),
    vis_mode="collision"
)

cam = scene.add_camera(
    res    = (1280, 960),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False
)

plane = scene.add_entity(gs.morphs.Plane(), vis_mode="collision")

scene.build()

df = pd.read_csv("genesis/data/test_position_array.csv")

for joint in robot.joints: 
    print(f"name: {joint.name}; idx: {joint.idx}; type: {joint.type}; DOF start: {joint.dof_start}; DOF end: {joint.dof_end}; DOF Count: {joint.dof_end - joint.dof_start}")

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
cam.start_recording()
robot.set_pos([0,0,0])
qpos = np.zeros(robot.get_qpos().shape[0])
# qpos[0:3] = [0, 0, 1.3]
qpos[3:7] = [1, 0, 0, 0]
y_offset = 1.1
for frame_idx, row in df.iterrows():
    # qpos = np.zeros(robot.get_qpos().shape[0])
    # print("qpos", qpos)
    # print(len(qpos))

    # Root pose
    qpos[0:3] = row[['z', 'y', 'x']]
    qpos[2] = qpos[2] + y_offset
    # x_sim = row[['x']]
    # y_sim = -row[['z']]
    # z_sim = row['y']
    # qpos[0:3] = [x_sim, y_sim, z_sim]
    # qpos[2] = row[['z']] + z_offset
    # qpos[3:7] = row[['qw', 'qx', 'qy', 'qz']]

    for csv_col, dof_list in csv_to_dof.items():
        for dof in dof_list:
            if dof in dof_idx_map:
                idx = dof_idx_map[dof] + 7
                qpos[idx] = row[csv_col]

    # print(len(qpos))
    # print(qpos)
    # print_qpos_mapping(robot)
    robot.set_qpos(qpos)
    scene.step()
    cam.render()

cam.stop_recording(save_to_filename='genesis/videos/test_video.mp4', fps=60)