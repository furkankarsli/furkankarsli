# Hi there, I'm Furkan Karslı! 👋
### Mechatronics Engineer | ROS2 Robotics & Distributed IoT Developer

<p align="left">
  <a href="https://linkedin.com/in/furkankarsli"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
  <a href="mailto:furknkrsli@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
</p>

---

## 🚀 About Me

I am a **Mechatronics Engineer** specializing in autonomous mobile robots (AMRs), robotic software architectures, and smart IoT ecosystems. My expertise lies at the intersection of hardware-software integration, control theory, and web interface visualization:

- **Robotics (ROS2)**: Experienced in designing modular software nodes, mission state machines (SMACH), behavior trees (`py_trees`), SLAM mapping, and sensor synchronization (LIDAR, IMU, encoders).
- **Embedded & IoT**: Designing secure, distributed IoT systems using ESP32, ESP-12E, and Raspberry Pi, communicating via UDP broadcast and authenticated REST HTTP APIs.
- **Web Dashboards & DSP**: Developing responsive interfaces (Flask, WebSockets) to visualize real-time sensor streams and robot state execution, as well as browser-based digital signal processing (Web Audio API).

---

## 🛠️ Tech Stack & Skills

<table>
  <tr>
    <td valign="top" width="50%">
      <h4>💻 Languages & Software</h4>
      <img src="https://img.shields.io/badge/C++-00599C?style=flat-square&logo=c%2B%2B&logoColor=white" alt="C++" />
      <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
      <img src="https://img.shields.io/badge/C-A8B9CC?style=flat-square&logo=c&logoColor=black" alt="C" />
      <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white" alt="Java" />
      <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" alt="JS" />
      <img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white" alt="HTML5" />
      <img src="https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white" alt="CSS3" />
    </td>
    <td valign="top" width="50%">
      <h4>🤖 Robotics & Systems</h4>
      <img src="https://img.shields.io/badge/ROS2-22314E?style=flat-square&logo=ros&logoColor=white" alt="ROS2" />
      <img src="https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black" alt="Linux" />
      <img src="https://img.shields.io/badge/Gazebo-FF8C00?style=flat-square&logo=gazebo&logoColor=white" alt="Gazebo" />
      <img src="https://img.shields.io/badge/Behavior_Trees-4B0082?style=flat-square" alt="Behavior Trees" />
      <img src="https://img.shields.io/badge/SMACH-4682B4?style=flat-square" alt="SMACH State Machines" />
    </td>
  </tr>
  <tr>
    <td valign="top" width="50%">
      <h4>🔌 Hardware & Engineering</h4>
      <img src="https://img.shields.io/badge/ESP32-E67E22?style=flat-square&logo=espressif&logoColor=white" alt="ESP32" />
      <img src="https://img.shields.io/badge/Raspberry_Pi-A22846?style=flat-square&logo=raspberry-pi&logoColor=white" alt="Rpi" />
      <img src="https://img.shields.io/badge/Arduino-00979D?style=flat-square&logo=arduino&logoColor=white" alt="Arduino" />
      <img src="https://img.shields.io/badge/PLC_TIA_Portal-0099FF?style=flat-square&logo=siemens&logoColor=white" alt="PLC" />
      <img src="https://img.shields.io/badge/KiCad-314CB0?style=flat-square&logo=kicad&logoColor=white" alt="KiCad" />
    </td>
    <td valign="top" width="50%">
      <h4>🌐 Web & Web-DSP</h4>
      <img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask" />
      <img src="https://img.shields.io/badge/WebSocket-010101?style=flat-square&logo=socket.io&logoColor=white" alt="WebSocket" />
      <img src="https://img.shields.io/badge/Web_Audio_API-9B59B6?style=flat-square" alt="Web Audio API" />
      <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite" />
    </td>
  </tr>
</table>



## 🌟 Featured Projects

### 1. [AMR Forklift Simulation & Autonomy (amr_forklift)](https://github.com/furkankarsli/amr_forklift)
An industry-standard ROS2 simulation and autonomy package for the **Nebula Forklift AMR**, featuring physics-based Gazebo integration and a safety-critical behavior tree.
- **Core Features**:
  - **Autonomy Behavior Tree**: Implemented using `py_trees` to monitor battery, manage automatic docking/charging states, and handle emergency safety stops.
  - **AMR Forklift URDF**: Customized forklift geometry with prismatic joints (`lift_joint`) and parameterized passive rollers.
  - **Nebula Arena**: Custom simulated world environment in Gazebo with multiple path networks.
- **Tech Stack**: `ROS2 (Humble)`, `Python (py_trees)`, `Xacro (URDF)`, `Gazebo`, `RViz2`.

### 2. [Distributed Industrial IoT Ecosystem](https://github.com/furkankarsli/fkstech-iot)
A multi-node telemetry system for industrial monitoring and automation control.
- **Architecture**:
  - **Telemetry Nodes**: ESP-12E microcontrollers reading MQ-Gas, Flame, Temperature, and Humidity sensors, broadcasting UDP packets.
  - **Central Gateway**: An ESP32 system (programmed in native ESP-IDF C using FreeRTOS) that handles UDP broadcasts and sends secure HTTP POST requests to the cloud.
  - **Cloud Dashboard**: A Python Flask web server connected to a SQLite database displaying real-time sensor streams and controlling local actuators (Relays, OLED display mode, alarm LEDs).
- **Tech Stack**: `ESP-IDF (C)`, `Arduino (C++)`, `FreeRTOS`, `Python (Flask)`, `SQLite`, `UDP/HTTP REST`.

### 3. [Signal Lab & Frequency Synthesizer](https://github.com/furkankarsli/ses)
An advanced client-side web synthesizer for generating audio frequencies and binaural/monaural wave entrainment structures.
- **Core Engine**: Implements a complete DSP graph using the Web Audio API with multi-oscillator modulation, dynamic stereo panning, and automatic clipping prevention via gain scheduling and compressor nodes.
- **Offline Rendering**: Utilizes `lamejs` and `OfflineAudioContext` to synthesize and encode custom frequency paths into high-quality MP3s directly in the browser.
- **Tech Stack**: `Vanilla JavaScript`, `Web Audio API (DSP)`, `HTML5 Canvas (Oscilloscope)`, `CSS3`.

### 4. [ROS2 Behavior Tree Autonomy Tutorial Workspace](./git_ros2_ws)
A robust ROS2 workspace implementing basic robot autonomy architectures using Behavior Trees and State Machines.
- **Packages**:
  - `robot_bt`: Custom C++ and Python executor managing action servers (`CleanArea.action`), cmd_vel publishers, and simulated battery/distance sensors.
  - `turtle_tasks`: Runs optimized Nav2 parameters (`nav2_params_optimized.yaml`) for differential drive AMRs executing complex BT tasks.
  - `turtlebot_autonomy`: Automates high-level missions using the SMACH state machine framework.
  - `SimpleExamplesForBehaviorTree`: Teaches the basics of `behaviortree_cpp`, `smach`, and `py_trees`.
- **Tech Stack**: `ROS2 (Humble)`, `Python`, `C++`, `Behavior Trees`, `SMACH`, `Nav2`, `Gazebo`.

---

## 💼 Experience & Education

```mermaid
timeline
    title Education & Professional Milestones
    September 2021 - June 2026 : Bursa Technical University <br> B.S. in Mechatronics Engineering <br> (Autonomous Systems, Robotics & Embedded Software)
    June 2025 - August 2025 : Birfen Elektrik Elektronik <br> Robotics Engineering Intern <br> (ROS2 Control, Gazebo AMR Simulation, Flask Behavior Tree Monitor)
    September 2025 - December 2025 : EYKA Otomasyon <br> Automation Engineering Intern <br> (TIA Portal PLC Programming, Panel Assembly, Mechanical Integration)
    February 2026 - Present : Teknofest Robolig Software Lead <br> Hexapod Robot Project <br> (Leg Kinematics, Electronic Systems, Torque Damping Integration)
```

---

## 📫 Let's Connect!

- 👔 **LinkedIn**: [linkedin.com/in/furkankarsli](https://linkedin.com/in/furkankarsli)
- ✉️ **Email**: [furknkrsli@gmail.com](mailto:furknkrsli@gmail.com)
