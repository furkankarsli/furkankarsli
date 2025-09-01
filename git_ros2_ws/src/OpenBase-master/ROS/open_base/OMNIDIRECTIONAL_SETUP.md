# OpenBase Omnidirectional Controller Setup

Bu dosya, OpenBase robot'un `omnidirectional_controllers` paketi ile nasıl kurulacağını ve çalıştırılacağını açıklar.

## 🚀 Kurulum

### 1. Gerekli Paketler

```bash
# omnidirectional_controllers paketini kur
cd ~/ros2_ws/src
git clone https://github.com/mateusmenezes95/omnidirectional_controllers.git
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install --packages-select omnidirectional_controllers
source install/setup.bash
```

### 2. OpenBase Paketini Build Et

```bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select open_base
source install/setup.bash
```

## 🎮 Çalıştırma

### Test Launch Dosyası (Önerilen)

```bash
# Test launch dosyasını çalıştır
ros2 launch open_base test_omnidirectional.launch.py
```

### Axebot Style Launch

```bash
# Axebot style launch ile çalıştır
ros2 launch open_base axebot_style.launch.py
```

## 🔧 Konfigürasyon

### Tekerlek Pozisyonları (URDF'den Hesaplandı)

- **Left Wheel**: `[0.03464101615, 0.02, 0]` (~60°)
- **Right Wheel**: `[-0.03464101615, 0.02, 0]` (~-60°)
- **Back Wheel**: `[0, -0.04, 0]` (180°)

### Robot Parametreleri

- **Robot Radius**: 0.04m (merkezden arka tekerleğe)
- **Wheel Radius**: 0.01355m (roller pozisyonundan)
- **Gamma**: 0.0° (arka tekerlek Y ekseninde)

## 🎯 Kontrol

### Topic'ler

- `/cmd_vel` - Standart geometry_msgs/Twist mesajları
- `/odom` - Odometry bilgisi
- `/joint_states` - Tekerlek durumları

### Hareket Komutları

```bash
# İleri hareket
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 10

# Yan hareket
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.5, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 10

# Dönme
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}" --rate 10

# Çapraz hareket
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3, y: 0.3, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}" --rate 10
```

## 🔍 Test ve Doğrulama

### 1. Controller Durumu

```bash
# Controller listesini kontrol et
ros2 control list_controllers

# Controller durumunu kontrol et
ros2 control list_controllers --state
```

### 2. Topic'leri Dinle

```bash
# Joint states
ros2 topic echo /joint_states

# Odometry
ros2 topic echo /odom

# Robot description
ros2 param get /robot_state_publisher robot_description
```

### 3. TF Tree

```bash
# TF tree'yi görüntüle
ros2 run tf2_tools view_frames
```

## 🚨 Sorun Giderme

### Controller Hatası

```bash
# Controller'ları yeniden başlat
ros2 control unload_controller omnidirectional_controller
ros2 control load_controller omnidirectional_controller

# Controller'ları spawn et
ros2 run controller_manager spawner omnidirectional_controller
```

### Gazebo Plugin Hatası

```bash
# Gazebo'yu yeniden başlat
pkill -f gazebo
ros2 launch open_base test_omnidirectional.launch.py
```

### Joint State Hatası

```bash
# Joint state broadcaster'ı yeniden başlat
ros2 control unload_controller joint_state_broadcaster
ros2 control load_controller joint_state_broadcaster
ros2 run controller_manager spawner joint_state_broadcaster
```

## 📊 Beklenen Çıktı

Başarılı kurulum sonrası:

```
[INFO] [controller_manager]: Loading controller 'joint_state_broadcaster'
[INFO] [controller_manager]: Loading controller 'omnidirectional_controller'
[INFO] [spawner]: Spawned controller 'joint_state_broadcaster'
[INFO] [spawner]: Spawned controller 'omnidirectional_controller'
[INFO] [gazebo_ros2_control]: Connected to service!! robot_state_publisher
[INFO] [gazebo_ros2_control]: Received urdf from param server, parsing...
```

## 🎯 Sonraki Adımlar

1. **Teleop**: Klavye veya joystick ile manuel kontrol
2. **Navigation**: Nav2 yığını ile otonom navigasyon
3. **SLAM**: Cartographer veya SLAM Toolbox ile haritalama
4. **Path Planning**: MoveIt2 ile hareket planlama

---

**Not**: Bu kurulum, OpenBase robot'un 3 tekerlekli omnidirectional hareket kabiliyetini tam olarak kullanmanızı sağlar.



