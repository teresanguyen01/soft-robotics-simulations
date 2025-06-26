import pandas as pd

# 1) load the CSV you just generated
df = pd.read_csv("angle_arrays/Apose_062325.csv")    # ← adjust to your actual path

# 2) pick exactly the DOFs you drove
channels = [
    "x","y","z","qw","qx","qy","qz",
    "abdomen_z_0","abdomen_z_1",
    "shoulder1_right_0","shoulder1_right_1",
    "shoulder1_left_0","shoulder1_left_1",
    "abdomen_x",
    "elbow_right","elbow_left",
    "hip_x_right_0","hip_x_right_1","hip_x_right_2",
    "hip_x_left_0","hip_x_left_1","hip_x_left_2",
    "knee_right","knee_left",
    "ankle_y_right_0","ankle_y_right_1",
    "ankle_y_left_0","ankle_y_left_1",
]

# 3) compute summary stats
stats = df[channels].agg(['min','mean','max','std']).T

# 4) print the stats table
pd.set_option('display.float_format', '{: .3f}'.format)
print(stats)
