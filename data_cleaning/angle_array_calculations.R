# import the necessary libraries
library(readr)
library(pracma)
library(dplyr)
library(tidyr)
library(data.table)

raise_rhand_mocap = read.csv("/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/data/raise_rhand_mocap_cleaned.csv")
raise_rhand_sensor = read.csv("/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/data/raise_rhand_sensor.csv")

colnames(raise_rhand_mocap)
head(raise_rhand_mocap)

sensor_dt <- as.data.table(raise_rhand_sensor)

setnames(sensor_dt, "Time..ms.", "time_ms")

start_time <- sensor_dt$time_ms[1]
sensor_dt[, time_ms := time_ms - start_time]

sensor_dt[, time_sec := time_ms / 1000]

head(sensor_dt[, .(time_ms, time_sec)])
head(sensor_dt)

headers <- c("time_ms",
             "abdomen_z", "abdomen_y", "abdomen_x",
             "hip_x_right", "hip_z_right", "hip_y_right", "knee_right", "ankle_y_right", "ankle_x_right",
             "hip_x_left", "hip_z_left", "hip_y_left", "knee_left", "ankle_y_left", "ankle_x_left",
             "shoulder1_right", "shoulder2_right", "elbow_right",
             "shoulder1_left", "shoulder2_left", "elbow_left")

units <- c("",
           "rad", "rad", "rad",
           "rad", "rad", "rad", "rad", "rad", "rad",
           "rad", "rad", "rad", "rad", "rad", "rad",
           "rad", "rad", "rad", "rad", "rad", "rad")

headers_with_units <- ifelse(units == "", headers, paste0(headers, " [", units, "]"))

n_rows <- nrow(raise_rhand_mocap)
angle_array <- data.frame(matrix(NA, nrow = n_rows, ncol = length(headers_with_units)))
colnames(angle_array) <- headers_with_units

angle_array$time_ms <- raise_rhand_mocap$time_ms

head(angle_array)

quat_to_euler <- function(qx, qy, qz, qw) {
  
  # roll (x)
  sinr_cosp <- 2 * (qw * qx + qy * qz)
  cosr_cosp <- 1 - 2 * (qx^2 + qy^2)
  roll <- atan2(sinr_cosp, cosr_cosp)
  
  # pitch (y)
  sinp <- 2 * (qw * qy - qz * qx)
  pitch <- ifelse(abs(sinp) >= 1, sign(sinp) * pi/2, asin(sinp))
  
  # yaw (z)
  siny_cosp <- 2 * (qw * qz + qx * qy)
  cosy_cosp <- 1 - 2 * (qy^2 + qz^2)
  yaw <- atan2(siny_cosp, cosy_cosp)
  
  return(c(roll, pitch, yaw))
}

quats <- raise_rhand_mocap %>% select(time_ms, qx = abdomen_X, qy = abdomen_Y, qz = abdomen_Z, qw = abdomen_W)

euler_matrix <- t(mapply(quat_to_euler, quats$qx, quats$qy, quats$qz, quats$qw))
euler_df <- as.data.frame(euler_matrix)
colnames(euler_df) <- c("abdomen_x [rad]", "abdomen_y [rad]", "abdomen_z [rad]")

angle_array$`abdomen_x [rad]` <- euler_df$`abdomen_x [rad]`
angle_array$`abdomen_y [rad]` <- euler_df$`abdomen_y [rad]`
angle_array$`abdomen_z [rad]` <- euler_df$`abdomen_z [rad]`

head(angle_array)

quats_hip <- raise_rhand_mocap %>% select(qx = right_thigh_X, qy = right_thigh_Y, qz = right_thigh_Z, qw = right_thigh_W)

euler_matrix_hip <- t(mapply(quat_to_euler, quats_hip$qx, quats_hip$qy, quats_hip$qz, quats_hip$qw))
euler_df_hip <- as.data.frame(euler_matrix_hip)
colnames(euler_df_hip) <- c("hip_x_right [rad]", "hip_y_right [rad]", "hip_z_right [rad]")

angle_array$`hip_x_right [rad]` <- euler_df_hip$`hip_x_right [rad]`
angle_array$`hip_y_right [rad]` <- euler_df_hip$`hip_y_right [rad]`
angle_array$`hip_z_right [rad]` <- euler_df_hip$`hip_z_right [rad]`

head(angle_array[, c("time_ms", "hip_x_right [rad]", "hip_y_right [rad]", "hip_z_right [rad]")])

"left_thigh_X" %in% colnames(raise_rhand_mocap)

quats_hip <- raise_rhand_mocap %>% select(qx = left_thigh_X, qy = left_thigh_Y, qz = left_thigh_Z, qw = left_thigh_W)
colnames(raise_rhand_mocap)
euler_matrix_hip <- t(mapply(quat_to_euler, quats_hip$qx, quats_hip$qy, quats_hip$qz, quats_hip$qw))
euler_df_hip <- as.data.frame(euler_matrix_hip)
colnames(euler_df_hip) <- c("hip_x_left [rad]", "hip_y_left [rad]", "hip_z_left [rad]")

angle_array$`hip_x_left [rad]` <- euler_df_hip$`hip_x_left [rad]`
angle_array$`hip_y_left [rad]` <- euler_df_hip$`hip_y_left [rad]`
angle_array$`hip_z_left [rad]` <- euler_df_hip$`hip_z_left [rad]`

head(angle_array[, c("time_ms", "hip_x_left [rad]", "hip_y_left [rad]", "hip_z_left [rad]")])

colnames(angle_array)

quats_knee_right <- raise_rhand_mocap %>% select(qx = right_shin_X, qy = right_shin_Y, qz = right_shin_Z, qw = right_shin_W)

quats_knee_left <- raise_rhand_mocap %>% select(qx = left_shin_X, qy = left_shin_Y, qz = left_shin_Z, qw = left_shin_W)

euler_knee_right <- t(mapply(quat_to_euler, quats_knee_right$qx, quats_knee_right$qy, quats_knee_right$qz, quats_knee_right$qw))
knee_right_angle <- as.data.frame(euler_knee_right)[,1]

euler_knee_left <- t(mapply(quat_to_euler, quats_knee_left$qx, quats_knee_left$qy, quats_knee_left$qz, quats_knee_left$qw))
knee_left_angle <- as.data.frame(euler_knee_left)[,1]

angle_array$`knee_right [rad]` <- knee_right_angle
angle_array$`knee_left [rad]` <- knee_left_angle

head(angle_array[, c("time_ms", "knee_right [rad]", "knee_left [rad]")])
colnames(angle_array)

quats_ankle_right <- raise_rhand_mocap %>% select(qx = right_foot_X, qy = right_foot_Y, qz = right_foot_Z, qw = right_foot_W)

euler_ankle_right <- t(mapply(quat_to_euler, quats_ankle_right$qx, quats_ankle_right$qy, quats_ankle_right$qz, quats_ankle_right$qw))
euler_df_ankle_right <- as.data.frame(euler_ankle_right)

angle_array$`ankle_x_right [rad]` <- euler_df_ankle_right[, 1]
angle_array$`ankle_y_right [rad]` <- euler_df_ankle_right[, 2]

head(angle_array[, c("time_ms", "ankle_x_right [rad]", "ankle_y_right [rad]")])

quats_ankle_left <- raise_rhand_mocap %>% select(qx = left_foot_X, qy = left_foot_Y, qz = left_foot_Z, qw = left_foot_W)

euler_ankle_left <- t(mapply(quat_to_euler, quats_ankle_left$qx, quats_ankle_left$qy, quats_ankle_left$qz, quats_ankle_left$qw))
euler_df_ankle_left <- as.data.frame(euler_ankle_left)

angle_array$`ankle_x_left [rad]` <- euler_df_ankle_left[, 1]
angle_array$`ankle_y_left [rad]` <- euler_df_ankle_left[, 2]

head(angle_array[, c("time_ms", "ankle_x_left [rad]", "ankle_y_left [rad]")])

quats_shoulder_right <- raise_rhand_mocap %>% select(qx = right_upper_arm_X, qy = right_upper_arm_Y, qz = right_upper_arm_Z, qw = right_upper_arm_W)
euler_shoulder_right <- t(mapply(quat_to_euler, quats_shoulder_right$qx, quats_shoulder_right$qy, quats_shoulder_right$qz, quats_shoulder_right$qw))

euler_df_shoulder_right <- as.data.frame(euler_shoulder_right)

angle_array$`shoulder1_right [rad]` <- euler_df_shoulder_right[, 2]
angle_array$`shoulder2_right [rad]` <- euler_df_shoulder_right[, 1]

head(angle_array[, c("time_ms", "shoulder1_right [rad]", "shoulder2_right [rad]")])

quats_shoulder_left <- raise_rhand_mocap %>% select(qx = left_upper_arm_X, qy = left_upper_arm_Y, qz = left_upper_arm_Z, qw = left_upper_arm_W)

euler_shoulder_left <- t(mapply(quat_to_euler, quats_shoulder_left$qx, quats_shoulder_left$qy, quats_shoulder_left$qz,
                                quats_shoulder_left$qw))
euler_df_shoulder_left <- as.data.frame(euler_shoulder_left)

angle_array$`shoulder1_left [rad]` <- euler_df_shoulder_left[, 2]
angle_array$`shoulder2_left [rad]` <- euler_df_shoulder_left[, 1]

head(angle_array[, c("time_ms", "shoulder1_left [rad]", "shoulder2_left [rad]")])

quats_elbow_right <- raise_rhand_mocap %>% select(qx = right_forearm_X, qy = right_forearm_Y, qz = right_forearm_Z, qw = right_forearm_W)
euler_df_elbow_right <- as.data.frame(t(mapply(quat_to_euler, quats_elbow_right$qx, quats_elbow_right$qy, quats_elbow_right$qz, quats_elbow_right$qw)))
angle_array$`elbow_right [rad]` <- euler_df_elbow_right[, 1]

quats_elbow_left <- raise_rhand_mocap %>% select(qx = left_forearm_X, qy = left_forearm_Y, qz = left_forearm_Z, qw = left_forearm_W)
euler_df_elbow_left <- as.data.frame(t(mapply(quat_to_euler, quats_elbow_left$qx, quats_elbow_left$qy, quats_elbow_left$qz, quats_elbow_left$qw)))
angle_array$`elbow_left [rad]` <- euler_df_elbow_left[, 1]

path <- file.path("~", "Documents", "Faboratory Stuff", "soft-robotics-simulations", "data", "angle_array_rhand_mocap.csv")
write.csv(angle_array, path, row.names = FALSE)