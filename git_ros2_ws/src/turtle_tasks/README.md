# TurtleBot3 Behavior Tree

Bu proje, TurtleBot3 robotu için modüler bir davranış ağacı (Behavior Tree) uygulamasıdır. Robot, görevleri otomatik olarak yapabilir, batarya seviyesini takip edebilir ve gerektiğinde şarj istasyonuna gidebilir.

## 🚀 Özellikler

- **Otomatik Görev Yönetimi**: Task1, Task2, Task3 görevlerini sırayla yapar
- **Akıllı Batarya Yönetimi**: 60 saniyede bir batarya kontrolü, kritik seviyede otomatik şarj
- **Modüler Yapı**: Yeni görevler kolayca eklenebilir
- **Hata Toleransı**: Navigasyon hatalarında otomatik retry
- **Kapsamlı Loglama**: Tüm işlemler detaylı olarak loglanır

## 🏗️ Mimari

### Ana Bileşenler

1. **CommandSubscriber**: `/robot_command` topic'inden komutları dinler
2. **BatteryMonitor**: Batarya seviyesini sürekli kontrol eder
3. **TaskExecutor**: Görevleri sırayla yönetir
4. **NavigationManager**: Robot hareketlerini kontrol eder

### Davranış Ağacı Yapısı

```
Servis Robotu (Parallel)
├── KomutDinleyici (CommandSubscriber)
└── Ana Mantık (Selector)
    ├── AcilŞarj (Sequence)
    │   ├── BataryaKontrol (BatteryMonitor)
    │   ├── sarjaGit (Navigate)
    │   ├── ŞarjBekle (Wait)
    │   └── ŞarjKomutunuTemizle (ClearCommand)
    ├── Task1 (Sequence)
    │   ├── task1KomutuVarMi? (CheckForCommand)
    │   ├── AyaGit_Task1 (Navigate)
    │   ├── Task1Bekle (Wait)
    │   └── Task1KomutunuTemizle (ClearCommand)
    ├── Task2 (Sequence)
    │   ├── task2KomutuVarMi? (CheckForCommand)
    │   ├── AyaGit_Task2 (Navigate)
    │   ├── Task2ABekle (Wait)
    │   ├── ByeGit_Task2 (Navigate)
    │   ├── Task2BBekle (Wait)
    │   └── Task2KomutunuTemizle (ClearCommand)
    ├── Task3 (Sequence)
    │   ├── task3KomutuVarMi? (CheckForCommand)
    │   ├── A'yaGit_Task3 (Navigate)
    │   ├── Task3ABekle (Wait)
    │   ├── B'yeGit_Task3 (Navigate)
    │   ├── Task3BBekle (Wait)
    │   ├── C'yeGit_Task3 (Navigate)
    │   ├── Task3CBekle (Wait)
    │   └── Task3KomutunuTemizle (ClearCommand)
    ├── Idle'aDön (Sequence)
    │   ├── idledaMi? (CheckLocation)
    │   └── idleaGit (Navigate)
    └── Bosta (Running)
```

## 📍 Konumlar

- **baslangic**: (0.0, 0.0) - Robot başlangıç noktası
- **sarj**: (0.2, 0.0) - Şarj istasyonu
- **idle**: (1.0, 0.0) - Bekleme noktası
- **A**: (2.0, 0.0) - Task A noktası
- **B**: (3.0, 0.0) - Task B noktası
- **C**: (4.0, 0.0) - Task C noktası

## ⚡ Batarya Sistemi

- **Normal Çalışma**: Robot görev yaparken 60 saniyede bir batarya kontrolü
- **Kritik Seviye**: Batarya %20'nin altına düşünce acil şarj tetiklenir
- **Şarj Süresi**: 10 saniye şarj ile batarya %100'e çıkar
- **Otomatik Döngü**: Şarj sonrası görev yarım kaldıysa devam eder

## 🎯 Görev Sistemi

### Mevcut Görevler

1. **Task1**: A konumuna git → 2 saniye bekle → tamamla
2. **Task2**: A konumuna git → 2 saniye bekle → B konumuna git → 2 saniye bekle → tamamla
3. **Task3**: A konumuna git → 2 saniye bekle → B konumuna git → 2 saniye bekle → C konumuna git → 2 saniye bekle → tamamla

### Görev Komutları

- `task1`: Task1'i başlat
- `task2`: Task2'yi başlat
- `task3`: Task3'ü başlat
- `sarj`: Şarj istasyonuna git
- `idle`: Idle konumuna git
- `stop`: Tüm görevleri durdur

## 🔧 Yeni Görev Ekleme

### 1. Navigate Behavior Oluştur

```python
go_to_new_location = Navigate(
    name="YeniKonumaGit", 
    node=node, 
    pose=POSES["yeni_konum"], 
    location_name="yeni_konum", 
    logger=logger
)
```

### 2. Wait Behavior Ekle

```python
wait_new_task = Wait(name="YeniGorevBekle", wait_time=5.0)
```

### 3. POSES'e Yeni Konum Ekle

```python
POSES = {
    # ... mevcut konumlar ...
    "yeni_konum": {'x': 5.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
}
```

### 4. Yeni Task Sequence Oluştur

```python
new_task_sequence = py_trees.composites.Sequence(name="YeniTask", memory=True)
new_task_sequence.add_children([
    CheckForCommand(name="yeniTaskKomutuVarMi?", expected_command="yeniTask"),
    go_to_new_location,
    wait_new_task,
    ClearCommand(name="YeniTaskKomutunuTemizle")
])
```

### 5. Ana Mantığa Ekle

```python
main_logic.add_children([
    emergency_charge,
    task1_sequence,
    task2_sequence, 
    task3_sequence,
    new_task_sequence,  # Yeni görev buraya
    return_to_idle_sequence,
    idle
])
```

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- ROS2 Humble
- TurtleBot3 Gazebo
- Nav2 Navigation Stack
- py_trees

### Kurulum

```bash
cd ~/ros2_ws/src
git clone <repository_url> turtle_tasks
cd ~/ros2_ws
colcon build --packages-select turtle_tasks
source install/setup.bash
```

### Çalıştırma

1. **Gazebo Simülasyonu Başlat:**
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

2. **Nav2 Navigation Stack Başlat:**
```bash
ros2 launch nav2_bringup bringup_launch.py map:=$HOME/map/my_turtlebot_map.yaml
```

3. **Behavior Tree Başlat:**
```bash
ros2 run turtle_tasks run_tree
```

4. **Command Publisher Başlat:**
```bash
ros2 run turtle_tasks command_publisher
```

## 📝 Log Sistemi

Tüm işlemler `logs/treeloglari.txt` dosyasına kaydedilir:

- **Batarya Durumu**: Her saniye batarya seviyesi ve konum
- **Komut İşleme**: Gelen komutlar ve işlenme durumları
- **Navigasyon**: Hedef konumlar ve hareket durumları
- **Hata Durumları**: Timeout, retry ve başarısızlık logları

## 🐛 Sorun Giderme

### Yaygın Problemler

1. **Robot Hareket Etmiyor**: Nav2 stack'in çalıştığından emin ol
2. **Batarya Kontrolü Çalışmıyor**: Behavior tree node'unun aktif olduğunu kontrol et
3. **Komutlar İşlenmiyor**: `/robot_command` topic'inin yayınlandığını doğrula

### Debug Komutları

```bash
# Node'ları listele
ros2 node list

# Topic'leri kontrol et
ros2 topic list
ros2 topic echo /robot_command

# Log dosyasını takip et
tail -f ~/ros2_ws/src/turtle_tasks/logs/treeloglari.txt
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi push edin (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 İletişim

Sorularınız için issue açın veya pull request gönderin.
