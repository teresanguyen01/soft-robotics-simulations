library(ggplot2)
library(readr)

angle_array <- read.csv("~/Documents/Faboratory Stuff/soft-robotics-simulations/data/angle_array_rhand_mocap.csv")

ggplot(angle_array, aes(x = time_ms)) +
  geom_line(aes(y = shoulder1_right, color = "shoulder1_right")) +
  geom_line(aes(y = shoulder2_right, color = "shoulder2_right")) +
  labs(title = "Right Shoulder Joint Angles Over Time", x = "Time (ms)", y = "Angle (rad)") +
  scale_color_manual(values = c("shoulder1_right" = "blue", "shoulder2_right" = "red")) +
  theme_minimal()

library(tidyr)

elbow_data <- angle_array %>%
  select(time_ms, elbow_right, elbow_left) %>%
  pivot_longer(cols = c(elbow_right, elbow_left), names_to = "joint", values_to = "angle")

ggplot(elbow_data, aes(x = time_ms, y = angle, color = joint)) +
  geom_line() +
  labs(
    title = "Elbow Joint Angles Over Time",
    x = "Time (ms)",
    y = "Angle (rad)"
  ) +
  theme_minimal()


ggplot(angle_array, aes(x = time_ms)) +
  geom_line(aes(y = knee_right, color = "knee_right")) +
  geom_line(aes(y = knee_left, color = "knee_left")) +
  labs(title = "Knee Angles over time", x = "Time (ms)", y = "Angle (rad)") +
  scale_color_manual(values = c("knee_right" = "blue", "knee_left" = "red")) +
  theme_minimal()

ggplot(angle_array, aes(x = time_ms, y = elbow_right)) +
  geom_line(color = "purple") +
  labs(title = "Knee Angle Right over time", x = "Time (ms)", y = "Angle (rad)") +
  theme_minimal()

ggplot(angle_array, aes(x = time_ms)) +
  geom_line(aes(y = elbow_right, color = "elbow_right")) +
  geom_line(aes(y = elbow_left, color = "elbow_left")) +
  labs(title = "Elbow Right & Left Angles over time", x = "Time (ms)", y = "Angle (rad)") +
  scale_color_manual(values = c("elbow_right" = "blue", "elbow_left" = "red")) +
  theme_minimal()

ggplot(angle_array, aes(x = time_ms, y = elbow_right)) +
  geom_line(color = "purple") +
  labs(title = "Elbow Right Angles over time", x = "Time (ms)", y = "Angle (rad)") +
  theme_minimal()


library(ggplot2)
library(readr)

angle_array <- read.csv("~/Documents/Faboratory Stuff/soft-robotics-simulations/data/angle_array_lhand_mocap.csv")

ggplot(angle_array, aes(x = time_ms)) +
  geom_line(aes(y = shoulder1_right, color = "shoulder1_right")) +
  geom_line(aes(y = shoulder2_right, color = "shoulder2_right")) +
  labs(title = "Right Shoulder Joint Angles Over Time", x = "Time (ms)", y = "Angle (rad)") +
  scale_color_manual(values = c("shoulder1_right" = "blue", "shoulder2_right" = "red")) +
  theme_minimal()

library(tidyr)

elbow_data <- angle_array %>%
  select(time_ms, elbow_right, elbow_left) %>%
  pivot_longer(cols = c(elbow_right, elbow_left), names_to = "joint", values_to = "angle")

ggplot(elbow_data, aes(x = time_ms, y = angle, color = joint)) +
  geom_line() +
  labs(
    title = "Elbow Joint Angles Over Time",
    x = "Time (ms)",
    y = "Angle (rad)"
  ) +
  theme_minimal()


ggplot(angle_array, aes(x = time_ms)) +
  geom_line(aes(y = elbow_right, color = "elbow_right")) +
  geom_line(aes(y = elbow_left, color = "elbow_left")) +
  labs(title = "Elbow Right & Left Angles over time", x = "Time (ms)", y = "Angle (rad)") +
  scale_color_manual(values = c("elbow_right" = "blue", "elbow_left" = "red")) +
  theme_minimal()

ggplot(angle_array, aes(x = time_ms, y = elbow_right)) +
  geom_line(color = "purple") +
  labs(title = "Elbow Right Angles over time", x = "Time (ms)", y = "Angle (rad)") +
  theme_minimal()
