# Turtlebot4 Obstacle Visualizer

This repository contains a ROS 2 node designed to detect obstacles in a robot's path. It can also function as a plugin to visualize fused LiDAR and camera data in real-time while the robot operates autonomously.

---

## 🚀 How to Use

Follow these steps to clone, build, and run the package in your ROS 2 workspace:

### 1. Clone the Repository
Navigate to the `src` directory of your workspace and clone this repository:
```bash
cd ~/turtlebot4_ws/src
git clone git@github.com:Onionsoupe/Turtlebot4-Obstacle-Visualizer.git
```

### 2. Build the Workspace
Navigate back to the root of your workspace and build the package:
```bash
cd ~/turtlebot4_ws
colcon build --packages-select turtlebot4_obstacle_visualizer
```

### 3. Source the Environment
Overlay your workspace environment so ROS 2 can locate the new node:
```bash
source install/setup.bash
```

### 4. Run the Obstacle Visualizer
Launch the node using the following command:
```bash
ros2 run obstacle_visualizer obstacle_visualizer_node
```

### 5. View the Output
Open `rqt_image_view` in a new terminal to visualize the fused obstacle data feed:
```bash
ros2 run rqt_image_view rqt_image_view
```

---

## 📺 Preview

![Turtlebot4 Visualizer](https://github.com)
