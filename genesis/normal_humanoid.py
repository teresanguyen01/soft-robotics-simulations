import os
os.environ['PYOPENGL_PLATFORM'] = 'glx'
import genesis as gs
import numpy as np 
gs.init(backend=gs.gpu)

scene = gs.Scene(show_viewer=True)
robot = scene.add_entity(
    gs.morphs.MJCF(file="genesis/xml/humanoid.xml"),
    vis_mode="collision"
)

scene.build()

# qpos_squat = np.array([0, 0, 0.596, 0.988015, 0, 0.154359, 0, 0, 0.4, 0, -0.25, -0.5, -2.5, -2.65, -0.8, 0.56, -0.25, -0.5, -2.5, -2.65, -0.8, 0.56, 0, 0, 0, 0, 0, 0])

# print(dir(robot))
# print(robot._joints)
# robot.set_qpos(robot.set)
print("init qpos", robot.init_qpos)
print("number of joints", robot.n_joints)
print(robot.get_qpos())

for i in range(1000):
    print(robot.get_qpos())

    scene.step()