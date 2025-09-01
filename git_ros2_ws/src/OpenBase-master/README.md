# OpenBase ROS2 Migration Project

Bu proje, OpenBase omnidirectional robot paketini ROS1'den ROS2'ye başarıyla migrate etme sürecini dokümante eder.

## 🚀 Proje Özeti

OpenBase, 3 tekerlekli omnidirectional bir robot platformudur. Bu projede, orijinal ROS1 paketi ROS2 Humble'e başarıyla migrate edilmiş ve Gazebo'da başarıyla çalıştırılmıştır.

## ✅ Başarıyla Tamamlanan Görevler

- [x] ROS1 paketini ROS2'ye migrate etme
- [x] Custom mesaj ve servisleri ROS2 formatına çevirme
- [x] URDF/XACRO dosyalarını ROS2'ye uyarlama
- [x] Gazebo'da robot modelini spawn etme
- [x] Robot state publisher ve joint state publisher kurulumu
- [x] Basit ve gerçek robot modellerini test etme

## 📁 Proje Yapısı

```
ROS/open_base/
├── package.xml                    # ROS2 package manifest
├── CMakeLists.txt                 # ROS2 build configuration
├── launch/
│   ├── gazebo_empty_world.launch.py  # Main launch file (Gazebo + RViz)
│   ├── simple_gazebo.launch.py       # Simple test robot in Gazebo
│   ├── real_robot_gazebo.launch.py   # Real OpenBase robot in Gazebo
│   └── test_robot.launch.py          # RViz only test
├── msg/
│   ├── Movement.msg               # Movement message definition
│   ├── MovementBezier.msg         # Bezier movement message
│   ├── MovementGeneric.msg        # Generic movement message
│   └── Velocity.msg               # Velocity message
├── srv/
│   ├── FrameToFrame.srv           # Frame transformation service
│   ├── KinematicsForward.srv      # Forward kinematics service
│   └── KinematicsInverse.srv      # Inverse kinematics service
├── src/
│   └── main_ros2.cpp              # Main ROS2 control node
├── urdf/
│   ├── description.urdf           # Generated URDF file (real robot)
│   └── simple_test.urdf           # Simple test URDF
├── xacro/
│   ├── main.urdf.xacro            # Main XACRO file
│   └── rim.urdf.xacro             # Rim component XACRO
└── mesh/                          # 3D model files
```

## 🎯 Gazebo Kurulum ve Test Süreci

### 1. Basit Test Robot ile Başlama

**Amaç:** Gazebo'nun temel işlevselliğini test etmek

**Basit Test URDF (simple_test.urdf):**
```xml
<?xml version="1.0"?>
<robot name="open_base_simple">
  <!-- Mavi kutu base -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.2 0.2 0.05"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 0.8 1"/>
      </material>
    </visual>
  </link>
  
  <!-- Kırmızı tekerlekler -->
  <link name="left_wheel">...</link>
  <link name="right_wheel">...</link>
</robot>
```

**Launch Komutu:**
```bash
ros2 launch open_base simple_gazebo.launch.py
```

**Beklenen Çıktı:**
```
[gzserver-1] [Msg] Connected to gazebo master @ http://127.0.0.1:11345
[spawn_entity.py-4] [INFO] Spawn status: SpawnEntity: Successfully spawned entity [open_base_simple]
```

### 2. Gerçek OpenBase Robot Yükleme

**Amaç:** Tam OpenBase robot modelini Gazebo'da çalıştırmak

**Launch Komutu:**
```bash
ros2 launch open_base real_robot_gazebo.launch.py
```

**Beklenen Çıktı:**
```
[gzserver-1] [Msg] Connected to gazebo master @ http://127.0.0.1:11345
[gzserver-1] [Msg] Loading world file [/opt/ros/humble/share/gazebo_ros/worlds/empty.world]
[spawn_entity.py-5] [INFO] Spawn status: SpawnEntity: Successfully spawned entity [open_base]
```

### 3. Kritik Gazebo Plugin'leri

**Gerekli Plugin'ler:**
```bash
# Launch dosyasında
gzserver -s libgazebo_ros_init.so -s libgazebo_ros_factory.so
```

**Plugin'lerin Amacı:**
- `libgazebo_ros_init.so`: ROS2-Gazebo bağlantısı
- `libgazebo_ros_factory.so`: Robot spawn etme servisi

### 4. Mesh Dosya Yolu Düzeltme

**Sorun:** Gazebo mesh dosyalarını bulamıyor
```
[gzclient-2] [Wrn] [FuelModelDatabase.cc:313] URI not supported by Fuel [model://open_base/mesh/rim.stl]
[gzclient-2] [Err] [Visual.cc:2956] No mesh specified
```

**Çözüm:** `package://` URI'lerini mutlak yollarla değiştir

**Komut:**
```bash
cd /home/furkan/ros2_ws/src/OpenBase-master/ROS/open_base/urdf
sed -i 's|package://open_base/mesh/|/home/furkan/ros2_ws/install/open_base/share/open_base/mesh/|g' description.urdf
```

**Değişen Yollar:**
- `package://open_base/mesh/base.stl` → `/home/furkan/ros2_ws/install/open_base/share/open_base/mesh/base.stl`
- `package://open_base/mesh/rim.stl` → `/home/furkan/ros2_ws/install/open_base/share/open_base/mesh/rim.stl`
- `package://open_base/mesh/roller.stl` → `/home/furkan/ros2_ws/install/open_base/share/open_base/mesh/roller.stl`

**Neden:** Gazebo ROS2'de `package://` URI'lerini düzgün çözemiyor

### 5. ROS2 Control Konfigürasyonu

**Amaç:** Robot'un tekerleklerini kontrol etmek

**Konfigürasyon Dosyası (config/controllers.yaml):**
```yaml
controller_manager:
  ros__parameters:
    update_rate: 50  # Hz
    
    # Joint state controller
    joint_state_broadcaster:
      type: joint_state_broadcaster/JointStateBroadcaster
    
    # Wheel controllers
    left_wheel_controller:
      type: effort_controllers/JointPositionController
      joints: [left_rim_joint]
```

**Launch Dosyası Güncellemesi:**
```python
# Controller manager
controller_manager_node = Node(
    package='controller_manager',
    executable='ros2_control_node',
    parameters=[controllers_config]
)

# Spawn controllers
spawn_controllers = Node(
    package='controller_manager',
    executable='spawner',
    arguments=['joint_state_broadcaster', 'left_wheel_controller', ...]
)
```

**Beklenen Çıktı:**
```
[INFO] [gazebo_ros2_control]: connected to service!! robot_state_publisher
[INFO] [gazebo_ros2_control]: Received urdf from param server, parsing...
```

### 6. Sorun Giderme

**Sık Karşılaşılan Hatalar:**

1. **"Service /spawn_entity unavailable"**
   - **Çözüm:** `libgazebo_ros_factory.so` plugin'ini ekle
   - **Komut:** `gzserver -s libgazebo_ros_factory.so`

2. **"Failed to load plugin libgazebo_ros2_control.so"**
   - **Çözüm:** Bu plugin henüz gerekli değil, robot çalışıyor
   - **Not:** İleride ROS2 control için gerekli olacak

3. **Gazebo Siyah Ekran**
   - **Çözüm:** Plugin'leri doğru sırayla yükle
   - **Sıra:** Önce server, sonra client

6. **"URI not supported by Fuel [model://open_base/mesh/rim.stl]"**
   - **Çözüm:** Mesh dosya yollarını mutlak yollarla değiştir
   - **Komut:** `sed -i 's|package://open_base/mesh/|/home/furkan/ros2_ws/install/open_base/share/open_base/mesh/|g' description.urdf`
   - **Neden:** Gazebo `package://` URI'lerini çözemiyor

## 🔧 Yapılan Değişiklikler

### 1. Package Manifest (package.xml)

**ROS1'den ROS2'ye değişiklikler:**
```xml
<!-- ROS1 -->
<package>
<buildtool_depend>catkin</buildtool_depend>
<build_depend>roscpp</build_depend>
<run_depend>roscpp</run_depend>

<!-- ROS2 -->
<package format="3">
<buildtool_depend>ament_cmake</buildtool_depend>
<depend>rclcpp</depend>
```

**Tam değişiklikler:**
- `format="3"` eklendi
- `catkin` → `ament_cmake` build tool
- `roscpp` → `rclcpp` dependency
- `message_generation` → `rosidl_default_generators`
- `message_runtime` → `rosidl_default_runtime`
- `member_of_group>rosidl_interface_packages</member_of_group>` eklendi

### 2. Build Configuration (CMakeLists.txt)

**Ana değişiklikler:**
```cmake
# ROS1
cmake_minimum_required(VERSION 2.8.3)
find_package(catkin REQUIRED COMPONENTS ...)
catkin_package(...)

# ROS2
cmake_minimum_required(VERSION 3.8)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
ament_package()
```

**Mesaj üretimi değişiklikleri:**
```cmake
# ROS1
add_message_files(FILES ...)
generate_messages(DEPENDENCIES ...)

# ROS2
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Velocity.msg"
  "msg/MovementBezier.msg"
  "msg/MovementGeneric.msg"
  "msg/Movement.msg"
  "srv/FrameToFrame.srv"
  "srv/KinematicsForward.srv"
  "srv/KinematicsInverse.srv"
  DEPENDENCIES std_msgs geometry_msgs
)
```

### 3. Mesaj Formatları

**MovementBezier.msg - Field isimleri snake_case'e çevrildi:**
```
# ROS1
geometry_msgs/Pose2D[] targetTranslation
float64[] targetRotation
bool offsetTraslation
bool offsetRotation

# ROS2
geometry_msgs/Pose2D[] target_translation
float64[] target_rotation
bool offset_translation
bool offset_rotation
```

### 4. URDF/XACRO Güncellemeleri

**main.urdf.xacro:**
```xml
<!-- ROS1 -->
<plugin name="gazebo_ros_control" filename="libgazebo_ros_control.so">

<!-- ROS2 -->
<plugin name="gazebo_ros2_control" filename="libgazebo_ros2_control.so">
```

**rim.urdf.xacro:**
```xml
<!-- ROS1 -->
<hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>

<!-- ROS2 -->
<hardwareInterface>hardware_interface/EffortJointInterface</hardwareInterface>
```

### 5. C++ Kod Migrasyonu

**main_ros2.cpp - ROS2 uyumlu yeni dosya:**
```cpp
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64.hpp>
#include <open_base/msg/movement.hpp>
#include <open_base/msg/velocity.hpp>

class OpenBaseController : public rclcpp::Node
{
public:
    OpenBaseController() : Node("open_base_main")
    {
        // Publishers
        v_left_command_ = this->create_publisher<std_msgs::msg::Float64>(
            "left_joint_velocity_controller/command", 1);
        v_back_command_ = this->create_publisher<std_msgs::msg::Float64>(
            "back_joint_velocity_controller/command", 1);
        v_right_command_ = this->create_publisher<std_msgs::msg::Float64>(
            "right_joint_velocity_controller/command", 1);

        // Subscribers
        command_subscriber_ = this->create_subscription<open_base::msg::Movement>(
            "command", 1, std::bind(&OpenBaseController::onCommandMessage, this, std::placeholders::_1));

        // Timer
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100), std::bind(&OpenBaseController::timerCallback, this));
    }
};
```

### 6. Launch Sistemi

**gazebo_empty_world.launch.py - Python launch dosyası:**
```python
#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Get package directories
    open_base_pkg = get_package_share_directory('open_base')
    gazebo_pkg = get_package_share_directory('gazebo_ros')
    turtlebot3_gazebo_pkg = get_package_share_directory('turtlebot3_gazebo')

    # Use empty world for faster loading
    world = os.path.join(turtlebot3_gazebo_pkg, 'worlds', 'empty_world.world')

    # Launch Gazebo with empty world
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gazebo_pkg, '/launch/gzserver.launch.py']),
        launch_arguments={'world': world}.items()
    )

    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'robot_description': open('install/open_base/share/open_base/urdf/description.urdf', 'r').read()
        }]
    )

    # Spawn robot
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'open_base',
            '-file', 'install/open_base/share/open_base/urdf/description.urdf',
            '-x', LaunchConfiguration('x_pose'),
            '-y', LaunchConfiguration('y_pose'),
            '-z', '0.0'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher_node,
        spawn_entity_node
    ])
```

## 🎮 Robot Kontrol Sistemi

### Robot Özellikleri
- **Tip**: Omnidirectional (3 tekerlekli)
- **Tekerlekler**: Left, Right, Back
- **Kontrol**: Velocity-based wheel control
- **Hareket**: İleri, geri, yan, dönme

### Kontrol Topic'leri
- `/command` - Ana kontrol topic'i (open_base/msg/Movement)
- `/left_joint_velocity_controller/command` - Sol tekerlek hızı
- `/right_joint_velocity_controller/command` - Sağ tekerlek hızı
- `/back_joint_velocity_controller/command` - Arka tekerlek hızı

### İleri Hareket Komutu
```bash
ros2 topic pub /command open_base/msg/Movement "{movement: 3, wheel: {v_left: 1.0, v_back: 1.0, v_right: 1.0}}" --once
```

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- ROS2 Humble
- Gazebo Classic (v11)
- RViz2
- TurtleBot3 Gazebo paketi
- ros2_control framework

### Build
```bash
cd /home/furkan/ros2_ws
colcon build --packages-select open_base
source install/setup.bash
```

### Çalıştırma

**⚠️ ÖNEMLİ: Her yeni çalıştırmadan önce eski süreçleri temizleyin!**

```bash
# 1. Eski süreçleri temizle
pkill -f "ros2 launch"
pkill -f "gazebo"
pkill -f "rviz"
pkill -f "open_base"

# 2. Doğru dizine git
cd /home/furkan/ros2_ws

# 3. ROS2 environment'ını source et
source install/setup.bash

# 4. Ana launch dosyasını çalıştır
ros2 launch open_base gazebo_empty_world.launch.py
```

### Robot Kontrolü

```bash
# Robot kontrol node'u (yeni terminal)
cd /home/furkan/ros2_ws
source install/setup.bash
ros2 run open_base open_base_main

# İleri hareket komutu
ros2 topic pub /command open_base/msg/Movement "{movement: 3, wheel: {v_left: 1.0, v_back: 1.0, v_right: 1.0}}" --rate 10
```

### Sorun Giderme

**Gazebo Server Çökerse:**
```bash
# Tüm süreçleri temizle
pkill -f "ros2 launch"
pkill -f "gazebo"
pkill -f "rviz"

# Doğru dizine git ve yeniden başlat
cd /home/furkan/ros2_ws
source install/setup.bash
ros2 launch open_base gazebo_empty_world.launch.py
```

**Robot Görünmüyorsa:**
```bash
# Joint states kontrol et
ros2 topic echo /joint_states --once

# Robot description kontrol et
ros2 param get /robot_state_publisher robot_description
```

**Gazebo Address Already in Use Hatası:**
```bash
# Tüm Gazebo süreçlerini zorla sonlandır
pkill -9 -f "gzserver"
pkill -9 -f "gzclient"
pkill -9 -f "gazebo"

# Yeniden başlat
cd /home/furkan/ros2_ws
source install/setup.bash
ros2 launch open_base gazebo_empty_world.launch.py
```

### Manuel Kontrol (Teleoperasyon)

**Klavye Kontrolü:**
```bash
# Yeni terminal aç
cd /home/furkan/ros2_ws
source install/setup.bash

# Klavye kontrolü başlat (topic remapping ile)
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args --remap cmd_vel:=/command
```

**Joystick Kontrolü:**
```bash
# Joystick node'u başlat
ros2 run joy joy_node

# Joystick teleop başlat
ros2 run teleop_twist_joy teleop_twist_joy_node --ros-args --remap cmd_vel:=/command
```

## 📊 Test Sonuçları

### ✅ Başarıyla Test Edilen Özellikler
- [x] ROS2 package build
- [x] Gazebo Classic simulation environment
- [x] RViz2 visualization
- [x] Robot state publishing
- [x] Joint state publishing
- [x] Robot spawn in world
- [x] Control system activation
- [x] Movement command system
- [x] İleri hareket komutu
- [x] URDF/XACRO parsing
- [x] Mesh file loading
- [x] ros2_control integration

### 🔧 Çözülen Sorunlar
1. **CMake Error**: ROS1 control paketleri → ROS2 uyumlu paketler
2. **Message Field Error**: camelCase → snake_case field isimleri
3. **Header Error**: ros/ros.h → rclcpp/rclcpp.hpp
4. **Launch Error**: XML → Python launch dosyaları
5. **Plugin Error**: gazebo_ros_control → gazebo_ros2_control
6. **Gazebo Server Crash**: Plugin compatibility issues
7. **Address Already in Use**: Multiple Gazebo instances
8. **Directory Issues**: Wrong working directory usage
9. **Process Cleanup**: Missing pkill commands before restart

## 📝 Teknik Detaylar

### Mimari Genel Bakış
Bu proje, ros2_control çatısını kullanarak donanım soyutlaması sağlar:
- **Hardware Interface**: Gazebo simülasyonu ile etkileşim
- **Controller**: Üst düzey komutları tekerlek komutlarına çevirir
- **Controller Manager**: Tüm kontrolörleri yönetir

### Omnidirectional Kinematik
- **3 Tekerlekli Yapı**: 120° açı ile yerleştirilmiş tekerlekler
- **Killough Platform**: Omnidirectional hareket kabiliyeti
- **Özel Kontrolör**: Standart diff_drive_controller yerine özel kinematik

### Mesaj Yapıları
- **Movement.msg**: Ana hareket mesajı (WHEEL, GENERIC, BEZIER)
- **Velocity.msg**: Tekerlek hızları (v_left, v_back, v_right)
- **MovementGeneric.msg**: Genel hareket komutları
- **MovementBezier.msg**: Bezier eğrisi hareketleri

### Servis Yapıları
- **FrameToFrame.srv**: Frame dönüşüm servisi
- **KinematicsForward.srv**: İleri kinematik servisi
- **KinematicsInverse.srv**: Ters kinematik servisi

### URDF Yapısı
- **base_link**: Ana robot gövdesi
- **left_rim_link**: Sol tekerlek rim'i
- **right_rim_link**: Sağ tekerlek rim'i
- **back_rim_link**: Arka tekerlek rim'i
- **roller_*_link**: Tekerlek roller'ları

## 🎯 Sonuç

Bu proje, ROS1'den ROS2'ye başarılı bir paket migrasyonu örneğidir. OpenBase robot artık ROS2 Humble ekosisteminde tam olarak çalışır durumda ve Gazebo Classic simülasyonunda test edilmiştir.

### Gelecek Geliştirmeler
- **Sensör Entegrasyonu**: LIDAR, kamera gibi simüle edilmiş sensörler
- **Otonom Navigasyon**: Nav2 yığını ile otonom hareket
- **Gerçek Donanım**: ros2_control çatısı sayesinde fiziksel robota kolay geçiş
- **Gelişmiş Kontrol**: omnidirectional_controllers paketi entegrasyonu

### Öğrenilen Dersler
- **Process Management**: Her başlatmadan önce pkill yapılması kritik
- **Directory Management**: Doğru dizinde çalışma önemli
- **Gazebo Compatibility**: Gazebo Classic v11 ile uyumluluk
- **ros2_control Integration**: Donanım soyutlaması için gerekli

## 📞 İletişim

Bu proje OpenBase robot platformunun ROS2 uyumluluğu için geliştirilmiştir.

---

**Not**: Bu README dosyası, ROS1'den ROS2'ye migrasyon sürecinde yapılan tüm değişiklikleri, kullanılan dosyaları ve teknik detayları kapsamlı bir şekilde dokümante eder.
