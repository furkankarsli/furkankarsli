# Turtle Tasks - Behavior Tree Robot Control

Bu paket, TurtleBot3 robotunu py_trees behavior tree kullanarak kontrol etmek için tasarlanmıştır.

## Kurulum

```bash
cd ~/ros2_ws
colcon build --packages-select turtle_tasks
source install/setup.bash
```

## Kullanım

### 1. Gazebo Simülasyonu Başlat
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

### 2. Nav2 Navigation Stack Başlat
```bash
ros2 launch nav2_bringup bringup_launch.py map:=$HOME/map/my_turtlebot_map.yaml
```

### 3. RViz2 Başlat
```bash
ros2 run rviz2 rviz2 -d /opt/ros/humble/share/nav2_bringup/rviz/nav2_default_view.rviz
```

### 4. Behavior Tree Başlat
```bash
ros2 run turtle_tasks run_tree
```

### 5. Command Publisher Başlat
```bash
ros2 run turtle_tasks command_publisher
```

## Komutlar

- `1`: Task1 - A'ya git, 2 saniye bekle
- `2`: Task2 - A'ya git, B'ye git, 2'şer saniye bekle  
- `3`: Task3 - A'ya git, B'ye git, C'ye git, 2'şer saniye bekle
- `i`: Idle konumuna git
- `s`: Robotu durdur
- `q`: Çıkış

## Sorun Giderme

### Robot Hareket Etmiyor

Eğer robot komutları alıyor ama hareket etmiyorsa:

1. **Nav2 Durumunu Kontrol Et:**

2. **Nav2 Action Server'ı Test Et:**

3. **Topic'leri Kontrol Et:**
```bash
ros2 topic list
ros2 topic echo /cmd_vel
ros2 topic echo /odom
```

4. **Action Server'ları Kontrol Et:**
```bash
ros2 action list
```

### Yaygın Sorunlar

1. **Nav2 çalışmıyor**: Nav2 launch dosyasını tekrar başlat
2. **Gazebo çalışmıyor**: Gazebo simülasyonunu tekrar başlat
3. **TF hatası**: Nav2'nin tamamen başlamasını bekle
4. **Action server bulunamadı**: Nav2 stack'inin tamamen yüklenmesini bekle

## Debug Araçları

- `run_tree`: Ana behavior tree'yi çalıştırır
- `command_publisher`: Robot komutlarını yayınlar

## Log Dosyaları

- `logs/treeloglari.txt`: Behavior tree logları
- `logs/run_tree.log`: Run tree logları
- `logs/command_publisher.log`: Command publisher logları

## Pozisyonlar

Pozisyonlar `turtle_tasks/poses.yaml` dosyasında tanımlanmıştır:

```yaml
poses:
  baslangic: {x: 0.0, y: 0.0, oz: 0.0, ow: 1.000}
  sarj: {x: 0.2, y: 0.0, oz: 0.0, ow: 1.000}
  idle: {x: 1.0, y: 0.0, oz: 0.0, ow: 1.000}
  A: {x: 2.0, y: 0.0, oz: 0.0, ow: 1.000}
  B: {x: 3.0, y: 0.0, oz: 0.0, ow: 1.000}
  C: {x: 4.0, y: 0.0, oz: 0.0, ow: 1.000}
```

## Bağımlılıklar

- ROS2 Humble
- py_trees
- py_trees_ros
- nav2_msgs
- geometry_msgs
- tf2_ros
- nav_msgs
