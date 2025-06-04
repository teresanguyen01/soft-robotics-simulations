# Load necessary packages
library(dplyr)
library(readr)
library(ggplot2)
library(tidyr)
library(corrr)
library(reshape2)

# Load data
sensor_data <- read_csv("/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/data/raise_rhand_sensor.csv", show_col_types=FALSE)
# remove all unnecessary headers
mocap_data <- read.csv("/Users/teresanguyen/Documents/Faboratory Stuff/soft-robotics-simulations/data/raise_rhand_mocap.csv", skip = 3)
mocap_data <- mocap_data[-1,]
head(sensor_data)

mocap_data <- mocap_data[, !(colnames(mocap_data) %in% c("Skeleton.002.Skeleton.002", "Skeleton.002.Skeleton.002.1", "Skeleton.002.Skeleton.002.2", "Skeleton.002.Skeleton.002.3", "Skeleton.002.Skeleton.002.4", "Skeleton.002.Skeleton.002.5", "Skeleton.002.Skeleton.002.6",   "dancepad.Marker.001.3_X",   "dancepad.Marker.001.3", "dancepad.Marker.001.4", "dancepad.Marker.001.5",
                                                         "dancepad.Marker.0010.3", "dancepad.Marker.0010.4", "dancepad.Marker.0010.5",
                                                         "dancepad.Marker.002.3", "dancepad.Marker.002.4", "dancepad.Marker.002.5",
                                                         "dancepad.Marker.003.3", "dancepad.Marker.003.4", "dancepad.Marker.003.5",
                                                         "dancepad.Marker.004.3", "dancepad.Marker.004.4", "dancepad.Marker.004.5",
                                                         "dancepad.Marker.005.3", "dancepad.Marker.005.4", "dancepad.Marker.005.5",
                                                         "dancepad.Marker.006.3", "dancepad.Marker.006.4", "dancepad.Marker.006.5",
                                                         "dancepad.Marker.007.3", "dancepad.Marker.007.4", "dancepad.Marker.007.5",
                                                         "dancepad.Marker.008.3", "dancepad.Marker.008.4", "dancepad.Marker.008.5",
                                                         "dancepad.Marker.009.3", "dancepad.Marker.009.4", "dancepad.Marker.009.5",
                                                         "dancepad.Marker.011.3", "dancepad.Marker.011.4", "dancepad.Marker.011.5", "dancepad", "dancepad.1", "dancepad.2", "dancepad.3", "dancepad.4",
                                                         "dancepad.5", "dancepad.6", "dancepad.Marker.001", "dancepad.Marker.001.1", "dancepad.Marker.001.2",
                                                         "dancepad.Marker.002", "dancepad.Marker.002.1", "dancepad.Marker.002.2", "dancepad.Marker.003",
                                                         "dancepad.Marker.003.1", "dancepad.Marker.003.2", "dancepad.Marker.004", "dancepad.Marker.004.1",
                                                         "dancepad.Marker.004.2", "dancepad.Marker.005", "dancepad.Marker.005.1", "dancepad.Marker.005.2",
                                                         "dancepad.Marker.006", "dancepad.Marker.006.1", "dancepad.Marker.006.2", "dancepad.Marker.007",
                                                         "dancepad.Marker.007.1", "dancepad.Marker.007.2", "dancepad.Marker.008", "dancepad.Marker.008.1",
                                                         "dancepad.Marker.008.2", "dancepad.Marker.009", "dancepad.Marker.009.1", "dancepad.Marker.009.2",
                                                         "dancepad.Marker.0010", "dancepad.Marker.0010.1", "dancepad.Marker.0010.2", "dancepad.Marker.011",
                                                         "dancepad.Marker.011.1", "dancepad.Marker.011.2"))]

colnames(mocap_data)
# Check result
head(mocap_data)

joint_map <- c(
  Skeleton.002.Ab = "abdomen",
  Skeleton.002.Chest = "chest",
  Skeleton.002.LShoulder = "left_shoulder",
  Skeleton.002.RShoulder = "right_shoulder",
  Skeleton.002.RFArm = "right_forearm",
  Skeleton.002.LShin = "left_shin",
  Skeleton.002.RShin = "right_shin",
  Skeleton.002.T10 = "t10",
  Skeleton.002.RBAK = "right_back",
  Skeleton.002.CLAV = "clavicle",
  Skeleton.002.STRN = "sternum",
  Skeleton.002.Head = "head",
  Skeleton.002.Neck = "neck",
  Skeleton.002.LHand = "left_hand",
  Skeleton.002.RHand = "right_hand",
  Skeleton.002.LThumb1 = "left_thumb1",
  Skeleton.002.LThumb2 = "left_thumb2",
  Skeleton.002.LThumb3 = "left_thumb3",
  Skeleton.002.LIndex1 = "left_index1",
  Skeleton.002.LIndex2 = "left_index2",
  Skeleton.002.LIndex3 = "left_index3",
  Skeleton.002.LMiddle1 = "left_middle1",
  Skeleton.002.LMiddle2 = "left_middle2",
  Skeleton.002.LMiddle3 = "left_middle3",
  Skeleton.002.LRing1 = "left_ring1",
  Skeleton.002.LRing2 = "left_ring2",
  Skeleton.002.LRing3 = "left_ring3",
  Skeleton.002.LPinky1 = "left_pinky1",
  Skeleton.002.LPinky2 = "left_pinky2",
  Skeleton.002.LPinky3 = "left_pinky3",
  Skeleton.002.RThumb1 = "right_thumb1",
  Skeleton.002.RThumb2 = "right_thumb2",
  Skeleton.002.RThumb3 = "right_thumb3",
  Skeleton.002.RIndex1 = "right_index1",
  Skeleton.002.RIndex2 = "right_index2",
  Skeleton.002.RIndex3 = "right_index3",
  Skeleton.002.RMiddle1 = "right_middle1",
  Skeleton.002.RMiddle2 = "right_middle2",
  Skeleton.002.RMiddle3 = "right_middle3",
  Skeleton.002.RRing1 = "right_ring1",
  Skeleton.002.RRing2 = "right_ring2",
  Skeleton.002.RRing3 = "right_ring3",
  Skeleton.002.RPinky1 = "right_pinky1",
  Skeleton.002.RPinky2 = "right_pinky2",
  Skeleton.002.RPinky3 = "right_pinky3",
  Skeleton.002.LFoot = "left_foot",
  Skeleton.002.LToe = "left_toe",
  Skeleton.002.RFoot = "right_foot",
  Skeleton.002.RToe = "right_toe",
  Skeleton.002.LFHD = "left_forehead",
  Skeleton.002.RBHD = "right_back_head",
  Skeleton.002.LBHD = "left_back_head",
  Skeleton.002.RFHD = "right_forehead",
  Skeleton.002.LUArm = "left_upper_arm",
  Skeleton.002.LFArm = "left_forearm",
  Skeleton.002.RUArm = "right_upper_arm",
  Skeleton.002.LASI = "left_asi",
  Skeleton.002.LPSI = "left_psi",
  Skeleton.002.RPSI = "right_psi",
  Skeleton.002.RASI = "right_asi",
  Skeleton.002.LThigh = "left_thigh",
  Skeleton.002.LANK = "left_ankle",
  Skeleton.002.LHEE = "left_heel",
  Skeleton.002.LTOE = "left_toe_marker",
  Skeleton.002.RThigh = "right_thigh",
  Skeleton.002.RANK = "right_ankle",
  Skeleton.002.RHEE = "right_heel",
  Skeleton.002.RTOE = "right_toe_marker",
  Skeleton.002.LTHI = "left_thigh_alt",
  Skeleton.002.LKNE = "left_knee",
  Skeleton.002.LTIB = "left_tibia",
  Skeleton.002.RTHI = "right_thigh_alt",
  Skeleton.002.RKNE = "right_knee",
  Skeleton.002.RTIB = "right_tibia",
  Skeleton.002.LFIN = "left_finger",
  Skeleton.002.RFIN = "right_finger",
  Skeleton.002.LSHO = "left_shoulder",
  Skeleton.002.LELB = "left_elbow",
  Skeleton.002.LWRB = "left_wrist_b",
  Skeleton.002.LWRA = "left_wrist_a",
  Skeleton.002.RSHO = "right_shoulder",
  Skeleton.002.RELB = "right_elbow",
  Skeleton.002.RUPA = "right_upper_arm",
  Skeleton.002.C7 = "7_cervical_vertebra",
  Skeleton.002.LUPA = "left_upper_arm",
  Skeleton.002.LFRM = "left_forearm",
  Skeleton.002.RWRB = "right_wrist_b",
  Skeleton.002.RWRA = "right_wrist_a",
  Skeleton.002.RFRM = "right_forearm"
  
)

# original joint names extracted
colnames(mocap_data)
# Remove suffixes like ".1", ".6", etc. from the original names
original_joint_names <- colnames(mocap_data)

clean_joint_names <- sub("\\.[0-9]+$", "", original_joint_names)

# Replace using the dictionary
renamed_joint_names <- ifelse(
  clean_joint_names %in% names(joint_map),
  joint_map[clean_joint_names],
  original_joint_names
)

# extract data type and axis for combination
axis <- unlist(mocap_data[2, ])

new_colnames <- paste(renamed_joint_names, axis, sep = "_")

# Remove spaces and NA
new_colnames <- gsub("NA", "", new_colnames)
new_colnames <- gsub("__", "_", new_colnames)

mocap_data <- mocap_data[-c(1:2), ]
colnames(mocap_data) <- new_colnames
colnames(mocap_data)[2] <- "time_ms"
colnames(mocap_data)[1] <- "Frame"

# Checks
head(mocap_data)
colnames(mocap_data)

mocap_data$time_ms <- as.numeric(mocap_data$time_ms) * 1000
head(mocap_data)

path <- file.path("~", "Documents", "Faboratory Stuff", "soft-robotics-simulations", "data", "raise_rhand_mocap_cleaned.csv")
write.csv(mocap_data, path, row.names = FALSE)