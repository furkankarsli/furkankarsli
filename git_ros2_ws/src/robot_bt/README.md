# 🤖 Kapsamlı Temizlik Robotu - ROS2 Behavior Tree

Bu proje, **Nav2 kullanmadan** sadece print ve sleep loglarıyla çalışan, gerçek bir temizlik robotu gibi davranan kapsamlı bir ROS2 Behavior Tree sistemi oluşturur.

## 🎯 Özellikler

### 🧹 Temizlik Özellikleri
- **Çoklu Temizlik Desenleri**: Zigzag, Spiral, Grid, Duvar Takibi
- **Akıllı Yüzey Algılama**: Halı, Parke, Mermer, Fayans
- **Adaptif Temizlik Modları**: Vakum + Fırça, Vakum + Islak, Vakum + Kuru
- **Gerçek Zamanlı İzleme**: Temizlik ilerlemesi, verimlilik analizi

### 🛡️ Güvenlik ve Güvenilirlik
- **Acil Durum Durdurma**: Anında tepki veren güvenlik sistemi
- **Robot Kurtarma**: Takılma durumlarında otomatik kurtarma
- **Sürekli İzleme**: Batarya, engel, yüzey tipi izleme
- **Hata Toleransı**: Paralel görev yapısı ile yüksek güvenilirlik

### 🔋 Enerji Yönetimi
- **Akıllı Batarya İzleme**: Kritik seviyelerde otomatik şarj
- **Enerji Optimizasyonu**: Yüzey tipine göre güç ayarlama
- **Şarj İstasyonu Yönetimi**: Otomatik bulma ve bağlanma

### 🧠 Akıllı Karar Verme
- **Öncelik Sistemi**: Acil durumlar > Güvenlik > Batarya > Temizlik
- **Paralel İşlemler**: Temizlik ve izleme aynı anda
- **Durum Bazlı Davranış**: Çevre koşullarına göre adaptasyon

## 🏗️ Sistem Mimarisi

### Behavior Tree Yapısı
```
MainFallback (Fallback)
├── EmergencySequence (Sequence)
│   ├── IsEmergencyStop
│   └── EmergencyStop
├── SafetySequence (Sequence)
│   ├── IsRobotStuck
│   └── UnstickRobot
├── BatteryManagementSequence (Sequence)
│   ├── IsBatteryCritical
│   ├── GoToDock
│   └── Charge
└── MainCleaningSequence (Sequence)
    ├── StartupChecks (Sequence)
    │   ├── IsRobotReady
    │   ├── InitializeSensors
    │   └── CheckEnvironment
    ├── CleaningAndMonitoring (Parallel)
    │   ├── CleaningTasks (Sequence)
    │   │   ├── SelectCleaningMode
    │   │   ├── ExecuteCleaningPattern
    │   │   └── MonitorCleaningProgress
    │   └── ContinuousMonitoring (Sequence)
    │       ├── MonitorBatteryLevel
    │       ├── MonitorObstacles
    │       ├── MonitorSurfaceType
    │       └── MonitorCleaningEfficiency
    └── PostCleaningSequence (Sequence)
        ├── ReturnToDock
        ├── GenerateCleaningReport
        └── WaitForNextTask
```

### Node Yapısı
- **bt_executor**: Ana Behavior Tree yöneticisi
- **emergency_publisher**: Acil durum simülasyonu
- **battery_state_publisher**: Batarya durumu simülasyonu
- **distance_sensor_publisher**: Engel algılama simülasyonu
- **cmd_vel_publisher**: Hareket komutları
- **clean_action_server**: Temizlik görevi sunucusu
- **move_action_server**: Hareket görevi sunucusu

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
```bash
# ROS2 Humble
sudo apt install ros-humble-py-trees ros-humble-py-trees-ros
```

### Build
```bash
cd ~/ros2_ws
colcon build --packages-select robot_bt
source install/setup.bash
```

### Çalıştırma
```bash
# Tüm sistemi başlat
ros2 launch robot_bt robot_bt_launch.py

# Veya tek tek node'ları başlat
ros2 run robot_bt bt_executor
ros2 run robot_bt emergency_publisher
ros2 run robot_bt battery_state_publisher
```

## 📊 Simülasyon Özellikleri

### 🔋 Batarya Simülasyonu
- Her saniye %0.5 düşer
- %15 altında kritik seviye
- Otomatik şarj simülasyonu

### 🚨 Acil Durum Simülasyonu
- %1 ihtimalle tetiklenir
- Anında robot durdurma
- Manuel iptal sistemi

### 🤖 Robot Takılma Simülasyonu
- %5 ihtimalle takılır
- Otomatik kurtarma algoritması
- 3 deneme hakkı

### 🧹 Temizlik Simülasyonu
- 4 farklı desen: Zigzag, Spiral, Grid, Duvar Takibi
- 20 m² alan temizleme
- Gerçek zamanlı ilerleme takibi

## 📈 Log Çıktıları

Sistem çalışırken şu tür loglar göreceksiniz:

```
🤖 Kapsamlı Temizlik Robotu Behavior Tree Executor başlatıldı!
📂 Behavior Tree yükleniyor: /path/to/main_bt.xml
✅ Behavior Tree başarıyla yüklendi!
🌳 Tree yapısı: MainFallback
✅ 20 behavior node kaydedildi
🚀 Behavior Tree çalıştırılıyor...
📋 Robot durumları:
  🚨 Acil durumlar (En yüksek öncelik)
  🛡️ Güvenlik kontrolleri
  🔋 Batarya yönetimi
  🧹 Ana temizlik döngüsü

✅ Robot çalışmaya hazır!
🔍 Sensörler başlatılıyor...
  📡 Ultrasonik sensörü başlatıldı
  📡 Infrared sensörü başlatıldı
  📡 Kamera sensörü başlatıldı
  📡 IMU sensörü başlatıldı
  📡 Encoder sensörü başlatıldı
✅ Tüm sensörler başlatıldı!

🌍 Çevre analizi yapılıyor...
  📊 Oda boyutu: 5m x 4m
  📊 Yüzey tipi: Karışık (halı + parke)
  📊 Engel sayısı: 3 adet
  📊 Aydınlatma: Yeterli
  📊 Sıcaklık: 22°C
✅ Çevre analizi tamamlandı!

🧹 Temizlik modu seçiliyor...
🎯 Seçilen yüzey: halı
🧹 Temizlik modu: Vakum + Fırça (Güçlü)

🔄 Temizlik deseni: zigzag
🔄 zigzag deseni: %5.0
🔄 zigzag deseni: %10.0
...
✅ Temizlik deseni tamamlandı!

📊 Temizlik ilerlemesi: %15.0 (3.0/20.0 m²)
📊 Temizlik ilerlemesi: %20.0 (4.0/20.0 m²)
...
✅ Tüm alan temizlendi!

🏠 Dock'a dönüş başladı...
🏠 Dock'a dönüş: %12.5
🏠 Dock'a dönüş: %25.0
...
✅ Dock'a ulaşıldı!

📋 Temizlik raporu oluşturuluyor...
📊 TEMİZLİK RAPORU:
  Temizlik süresi: 45 dakika
  Temizlenen alan: 20 m²
  Kullanılan enerji: 2.3 kWh
  Engel sayısı: 3 adet
  Yüzey tipleri: Halı, Parke, Mermer
  Verimlilik: %85
  Temizlik modu: Karışık
✅ Rapor oluşturuldu!

⏰ Sonraki görev bekleniyor...
⏰ Bekleme: 9 saniye kaldı
⏰ Bekleme: 8 saniye kaldı
...
✅ Bekleme tamamlandı, yeni görev başlatılıyor!
```

## 🔧 Özelleştirme

### Behavior Tree Düzenleme
`behavior_trees/main_bt.xml` dosyasını düzenleyerek:
- Yeni davranışlar ekleyebilirsiniz
- Öncelik sırasını değiştirebilirsiniz
- Paralel görevler ekleyebilirsiniz

### Behavior Node'ları Özelleştirme
`robot_bt/behavior_nodes.py` dosyasında:
- Yeni condition node'ları ekleyebilirsiniz
- Action node'larını özelleştirebilirsiniz
- Simülasyon parametrelerini değiştirebilirsiniz

### Simülasyon Parametreleri
- **Batarya düşme hızı**: `battery_state_publisher.py`
- **Acil durum olasılığı**: `emergency_publisher.py`
- **Takılma olasılığı**: `behavior_nodes.py` - `IsRobotStuck`
- **Temizlik süreleri**: `behavior_nodes.py` - `ExecuteCleaningPattern`

## 🎮 Test Senaryoları

### Senaryo 1: Normal Temizlik
```bash
ros2 launch robot_bt robot_bt_launch.py
# Robot normal temizlik döngüsünü tamamlar
```

### Senaryo 2: Acil Durum Testi
```bash
# Emergency publisher'da olasılığı artırın
# %1 yerine %50 yapın
```

### Senaryo 3: Düşük Batarya Testi
```bash
# Battery publisher'da düşme hızını artırın
# 0.5 yerine 5.0 yapın
```

### Senaryo 4: Takılma Testi
```bash
# Behavior nodes'da takılma olasılığını artırın
# 0.05 yerine 0.5 yapın
```

## 📝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje Apache-2.0 lisansı altında lisanslanmıştır.

## 👨‍💻 Geliştirici

**Furkan** - furknkrsli@gmail.com

---

**Not**: Bu proje eğitim amaçlıdır ve gerçek robotlarda kullanılmadan önce kapsamlı testler yapılmalıdır.
