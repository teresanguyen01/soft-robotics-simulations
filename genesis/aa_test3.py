import os
os.environ['PYOPENGL_PLATFORM'] = 'glx'
import genesis as gs
import numpy as np
import pandas as pd
import time

gs.init(backend=gs.gpu)

scene = gs.Scene(
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        res=(1280, 960),
        camera_pos=(3.5, 0.0, 2.5),
        camera_lookat=(0.0, 0.0, 0.5),
        camera_fov=40,
        max_FPS=60,
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,
        world_frame_size=1.0,
        show_link_frame=False,
        show_cameras=False,
        plane_reflection=True,
        ambient_light=(0.1, 0.1, 0.1),
    ),
    renderer=gs.renderers.Rasterizer()
)

robot = scene.add_entity(
    gs.morphs.MJCF(file="genesis/xml/humanoid.xml"),
    vis_mode="collision"
)

cam = scene.add_camera(
    res=(1280, 960),
    pos=(5, 0.0, 2.5),
    lookat=(0, 0, 0.5),
    fov=30,
    GUI=False
)

plane = scene.add_entity(gs.morphs.Plane(), vis_mode="collision")

scene.build()

df = pd.read_csv("genesis/data2/aa_double_arm_lat (2).csv")

dof_names = []
for joint in robot.joints:
    count = joint.dof_end - joint.dof_start
    if joint.name == "root":
        continue
    if count == 1:
        dof_names.append(joint.name)
    else:
        for i in range(count):
            dof_names.append(f"{joint.name}_{i}")

dof_idx_map = {name: i for i, name in enumerate(dof_names)}

cam.start_recording()
robot.set_pos([0, 0, 0])
qpos = np.zeros(robot.get_qpos().shape[0])
y_offset = 1.15
qpos[3:7] = [1, 0, 0, 0]

for _, row in df.iterrows():
    qpos[0:3] = row[['z', 'y', 'x']].values
    qpos[2] += y_offset
    for dof_name, dof_idx in dof_idx_map.items():
        if dof_name in row:
            if dof_idx + 7 == 15: 
                print("dof name", dof_name)
            qpos[dof_idx + 7] = row[dof_name]
    # qpos[8] = 0.14122
    # qpos[15] = 0
    # qpos[11:13] = [0.030455,0.1468112]
    # qpos[16:19] = [0, 0, 0]
    # qpos[19:22] = [0, 0, 0]
    robot.set_qpos(qpos)
    scene.step()
    cam.render()

cam.stop_recording(save_to_filename='genesis/videos2/double_arm_lat.mp4', fps=60)