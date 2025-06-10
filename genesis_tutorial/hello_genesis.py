# removes the OpenGL error 
import os
os.environ['PYOPENGL_PLATFORM'] = 'glx'
import genesis as gs
# backend device -- NVIDIA GeForce RTX 4090
gs.init(backend=gs.gpu, precision='64')

# all objects are placed into the scene 
scene = gs.Scene(
    show_viewer = True,
    viewer_options = gs.options.ViewerOptions(
        res           = (1280, 960),
        camera_pos    = (3.5, 0.0, 2.5),
        camera_lookat = (0.0, 0.0, 0.5),
        camera_fov    = 40,
        max_FPS       = 60,
    ),
    vis_options = gs.options.VisOptions(
        show_world_frame = True,
        world_frame_size = 1.0,
        show_link_frame  = False,
        show_cameras     = False,
        plane_reflection = True,
        ambient_light    = (0.1, 0.1, 0.1),
    ),
    renderer=gs.renderers.Rasterizer(),
)

# all objects are represented as an entity -- OOP
plane = scene.add_entity(gs.morphs.Plane())

# can specify position and scale
franka = scene.add_entity(
    gs.morphs.MJCF(
        file='genesis_tutorial/assets/xml/universal_robots_ur5e/ur5e.xml',
        pos   = (0, 0, 0),
        euler = (0, 0, 90), # we follow scipy's extrinsic x-y-z rotation convention, in degrees,
        quat  = (1.0, 0.0, 0.0, 0.0), # we use w-x-y-z convention for quaternions,
        scale = 1.0
    ),
)

cam = scene.add_camera(
    res    = (1280, 960),
    pos    = (3.5, 0.0, 2.5),
    lookat = (0, 0, 0.5),
    fov    = 30,
    GUI    = False
)

# we can alsop use gs.morphs.Terrain to train the humanoid to walk through different terains

scene.build()

cam.start_recording()
import numpy as np

for i in range(120):
    scene.step()
    cam.set_pose(
        pos    = (3.0 * np.sin(i / 60), 3.0 * np.cos(i / 60), 2.5),
        lookat = (0, 0, 0.5),
    )
    cam.render()

cam.stop_recording(save_to_filename='genesis_tutorial/videos/test_video1.mp4', fps=60)