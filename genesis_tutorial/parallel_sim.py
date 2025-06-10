import torch
import os
os.environ['PYOPENGL_PLATFORM'] = 'glx'
import genesis as gs

gs.init(backend=gs.gpu)

scene = gs.Scene(
    show_viewer   = True,
    rigid_options = gs.options.RigidOptions(
        dt                = 0.01,
    ),
)

plane = scene.add_entity(
    gs.morphs.Plane(),
)

franka = scene.add_entity(
    gs.morphs.MJCF(file="genesis_tutorial/assets/xml/franka_emika_panda/panda.xml"),
)

scene.build(n_envs=100, env_spacing=(1.0,1.0))

# control all the robots
franka.control_dofs_position(
    torch.tile(
        torch.tensor([0, 0, 0, -1.0, 0, 0, 0, 0.02, 0.02], device=gs.device), (100, 1)
    ),
)

for i in range(1000):
    scene.step()