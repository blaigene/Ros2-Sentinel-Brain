# Sentinel Brain: Autonomous Mission Control System 🤖⚡

![ROS2](https://img.shields.io/badge/ROS2-Humble-22314E?logo=ros)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)
![AI-Ready](https://img.shields.io/badge/Architecture-AI--Ready-00C7B7)

**Sentinel Brain** is an autonomous mission control architecture built with **ROS2 (Python)**. Developed as the capstone project for an Industrial Programming Micro-credential in ROS2, this repository implements the high-level decision-making layer of an inspection robot ("Sentinel"). 

Designed with an **AI-first mindset**, this architecture provides a robust, state-driven foundation (managing waypoints, battery levels, and telemetry) ready to be integrated with advanced path-planning algorithms, computer vision pipelines, or Reinforcement Learning policies.

## 🎯 Project Overview

The system acts as the "brain" of the Sentinel robot, reading a warehouse inspection mission from a configuration file and executing it autonomously. It dynamically adapts its behavior based on real-time simulated telemetry (battery levels), managing the trade-off between completing inspection jobs and safely returning to the charging dock.

### Key Features
* **State-Driven Autonomy:** The `mission_control_client` intelligently pauses, resumes, or aborts missions based on real-time sensor data (e.g., dropping below a 30% battery threshold).
* **Asynchronous Action Execution:** Uses custom ROS2 Action Servers to handle complex, long-running tasks like point-to-point navigation, providing real-time progress feedback.
* **Service-Oriented Architecture:** Implements a decoupled incident reporting system using custom ROS2 Services.
* **Data-Driven Configuration:** Missions (waypoints, home base, speeds) are loaded dynamically via YAML files, making the system highly scalable and easy to connect to higher-level AI task planners.

## 🏗️ System Architecture

The project consists of several interacting ROS2 nodes that demonstrate standard industrial communication patterns:

1. **`mission_control_client` (The Decision Maker):** * The core of the system. It loads the `mission_file.yaml`, subscribes to the battery state, and dispatches single-waypoint goals. It includes threading and event synchronization to manage the execution loop asynchronously.
2. **`patrol_action_server` (The Actuator):**
   * Exposes the custom `Patrol.action`. It simulates robot movement to coordinates `(x, y)`, providing continuous feedback on task progress.
3. **`status_node` (The Sensor):**
   * Simulates critical telemetry by publishing the remaining battery level (`Float32`) via a Publisher/Subscriber model.
4. **`logger_server` & `incident_reporter` (The Comms):**
   * A Client-Service pair utilizing the custom `LogIncident.srv` for asynchronous reporting of anomalies or mission events.

## 🧠 AI Integration Potential

While this repository focuses on the ROS2 infrastructure, the modular design is deliberately structured to bridge the gap between AI and Robotics:

* **High-Level Task Planning:** The YAML mission parser can be easily replaced by a Large Language Model (LLM) or an AI planner generating dynamic waypoints based on semantic scene understanding.
* **RL / Navigation:** The Action Server (`Patrol`) can serve as the interface for a Reinforcement Learning policy controlling the actual motor commands (`cmd_vel`).
* **Computer Vision:** The incident reporting service (`LogIncident.srv`) is perfectly positioned to receive triggers from a YOLO/CNN node detecting anomalies (e.g., obstacles, fires, or specific objects) during the patrol.

## 🚀 Getting Started

### Prerequisites
* ROS2 (Humble or Iron recommended)
* Python 3
* `colcon` build system

### Installation & Build
Clone the repository into your ROS2 workspace `src` folder:

```bash
cd ~/ros2_ws/src
git clone [https://github.com/YOUR_USERNAME/sentinel_brain.git](https://github.com/YOUR_USERNAME/sentinel_brain.git)
cd ~/ros2_ws
colcon build --packages-select sentinel_brain sentinel_interfaces
source install/setup.bash

### Launching the System
Launch the complete autonomous ecosystem (Mission Control, Action Server, and Status Simulation) with a single command:

```bash
ros2 launch sentinel_brain session10_mission.launch.py

### Expected Output

The terminal will display the asynchronous decision-making process: loading the mission, dispatching the robot to the first shelf (`red_shelf`), publishing battery status, and eventually returning to the dock when the battery drops below the safe threshold.

### 🛠️ Tech Stack & Concepts Learned

* **Framework:** ROS2 (Python) / `ament_python`
* **Communication:** Publishers/Subscribers, Custom Actions (`Patrol.action`), Custom Services (`LogIncident.srv`).
* **Tooling:** ROS2 Launch (`launch.py`), YAML configurations, Threading/Synchronization in Python.
* **Domain:** Autonomous Systems, State Management, Industrial Robotics.

---
*This project was completed as part of the Micro-credential in Industrial Programming (ROS2) at the Escola Politècnica Superior (EPS), Universitat de Lleida (UdL).*