import os
os.environ['PYOPENGL_PLATFORM'] = 'glx'
import genesis as gs
import numpy as np 
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

scene.build()

cam.start_recording()

# qpos_squat = np.array([0, 0, 0.596, 0.988015, 0, 0.154359, 0, 0, 0.4, 0, -0.25, -0.5, -2.5, -2.65, -0.8, 0.56, -0.25, -0.5, -2.5, -2.65, -0.8, 0.56, 0, 0, 0, 0, 0, 0])

# print(dir(robot))
# print(robot._joints)
# robot.set_qpos(robot.set)
print("init qpos", robot.init_qpos)
print("number of joints", robot.n_joints)
print(robot.get_qpos())

for i in range(200):
    print(robot.get_qpos())
    scene.step()
    cam.render()

cam.stop_recording(save_to_filename='genesis/videos/loading_in_humanoid.mp4', fps=60)
