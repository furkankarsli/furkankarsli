import rclpy
import py_trees
import py_trees_ros
import py_trees.behaviour
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Bool, String, Int32, Float32
from geometry_msgs.msg import Twist
import time
import random
import math

class BaseBehaviorNode(py_trees.behaviour.Behaviour):
    """Tüm behavior node'lar için temel sınıf"""
    
    def __init__(self, name):
        super().__init__(name=name)
        self.log_pub = None
        self.node = None
        
    def setup(self, **kwargs):
        self.node = kwargs.get('node')
        if self.node:
            self.log_pub = self.node.create_publisher(String, 'system_log', 10)
    
    def log_message(self, message, level="INFO"):
        """Log mesajı gönder"""
        if self.log_pub:
            msg = String()
            timestamp = time.strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] [{level:8}] [{self.name:12}] {message}"
            msg.data = log_entry
            self.log_pub.publish(msg)
        
        # Console'a da yaz
        if level == "ERROR":
            print(f"❌ {self.name}: {message}")
        elif level == "WARN":
            print(f"⚠️ {self.name}: {message}")
        else:
            print(f"ℹ️ {self.name}: {message}")

# =============================================================================
# CONDITION NODES (Durum Kontrolleri)
# =============================================================================

class IsEmergencyStop(BaseBehaviorNode):
    """Acil durum butonuna basılıp basılmadığını kontrol eder"""
    
    def __init__(self, name="IsEmergencyStop"):
        super().__init__(name=name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.emergency_stop = False
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                Bool, 'emergency_stop', self.emergency_callback, 10)
    
    def emergency_callback(self, msg):
        self.emergency_stop = msg.data
        
    def update(self):
        if self.emergency_stop:
            self.log_message("🚨 ACİL DURUM DURDURMA AKTİF!", "ERROR")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsRobotStuck(BaseBehaviorNode):
    """Robotun takılıp takılmadığını kontrol eder"""
    
    def __init__(self, name="IsRobotStuck"):
        super().__init__(name=name)
        self.stuck_time = 0
        self.last_position = (0, 0)
        self.stuck_threshold = 10.0  # 10 saniye
        self.is_tangled = False
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                Bool, 'tangled_state', self.tangled_callback, 10)
    
    def tangled_callback(self, msg):
        self.is_tangled = msg.data
        
    def update(self):
        # Takılma durumu veya simülasyon
        if self.is_tangled or random.random() < 0.05:
            self.log_message("🤖 Robot takıldı!", "WARN")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsBatteryCritical(BaseBehaviorNode):
    """Batarya seviyesinin kritik olup olmadığını kontrol eder"""
    
    def __init__(self, name="IsBatteryCritical", critical_threshold=15.0):
        super().__init__(name=name)
        self.critical_threshold = critical_threshold
        self.current_battery = 100.0
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                BatteryState, 'battery_state', self.battery_callback, 10)
    
    def battery_callback(self, msg):
        self.current_battery = msg.percentage * 100.0
        
    def update(self):
        if self.current_battery <= self.critical_threshold:
            self.log_message(f"🔋 Kritik batarya seviyesi: {self.current_battery:.1f}%", "WARN")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsBinFull(BaseBehaviorNode):
    """Toz haznesinin dolu olup olmadığını kontrol eder"""
    
    def __init__(self, name="IsBinFull"):
        super().__init__(name=name)
        self.is_bin_full = False
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                Bool, 'bin_state', self.bin_callback, 10)
    
    def bin_callback(self, msg):
        self.is_bin_full = msg.data
        
    def update(self):
        if self.is_bin_full:
            self.log_message("🗑️ Toz haznesi dolu!", "WARN")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsLocalizationError(BaseBehaviorNode):
    """Konum hatası olup olmadığını kontrol eder"""
    
    def __init__(self, name="IsLocalizationError"):
        super().__init__(name=name)
        self.is_localization_error = False
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                Bool, 'localization_error', self.localization_callback, 10)
    
    def localization_callback(self, msg):
        self.is_localization_error = msg.data
        
    def update(self):
        if self.is_localization_error:
            self.log_message("📍 Konum hatası tespit edildi!", "WARN")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsSensorError(BaseBehaviorNode):
    """Sensör hatası olup olmadığını kontrol eder"""
    
    def __init__(self, name="IsSensorError"):
        super().__init__(name=name)
        self.sensor_status = "OK"
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                String, 'sensor_status', self.sensor_callback, 10)
    
    def sensor_callback(self, msg):
        self.sensor_status = msg.data
        
    def update(self):
        if self.sensor_status != "OK":
            self.log_message(f"📡 Sensör hatası: {self.sensor_status}", "WARN")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsOverheating(BaseBehaviorNode):
    """Aşırı ısınma durumunu kontrol eder"""
    
    def __init__(self, name="IsOverheating", max_temp=80.0):
        super().__init__(name=name)
        self.max_temp = max_temp
        self.current_temp = 25.0
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                Float32, 'temperature_status', self.temp_callback, 10)
    
    def temp_callback(self, msg):
        self.current_temp = msg.data
        
    def update(self):
        if self.current_temp >= self.max_temp:
            self.log_message(f"🌡️ Aşırı ısınma: {self.current_temp:.1f}°C", "WARN")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class IsRobotReady(BaseBehaviorNode):
    """Robotun çalışmaya hazır olup olmadığını kontrol eder"""
    
    def __init__(self, name="IsRobotReady"):
        super().__init__(name=name)
        self.ready_checks = {
            'sensors': False,
            'motors': False,
            'cleaning_system': False
        }
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        
    def update(self):
        # Simülasyon: Tüm sistemleri kontrol et
        self.ready_checks['sensors'] = True
        self.ready_checks['motors'] = True
        self.ready_checks['cleaning_system'] = True
        
        if all(self.ready_checks.values()):
            self.log_message("✅ Robot çalışmaya hazır!", "INFO")
            return py_trees.common.Status.SUCCESS
        else:
            self.log_message("❌ Robot henüz hazır değil!", "WARN")
            return py_trees.common.Status.FAILURE

# =============================================================================
# ACTION NODES (Eylem Düğümleri)
# =============================================================================

class EmergencyStop(BaseBehaviorNode):
    """Acil durum durdurma işlemini gerçekleştirir"""
    
    def __init__(self, name="EmergencyStop"):
        super().__init__(name=name)
        self.stopped = False
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.cmd_vel_pub = self.node.create_publisher(Twist, 'cmd_vel', 10)
        
    def initialise(self):
        self.stopped = False
        
    def update(self):
        if not self.stopped:
            # Robotu durdur
            stop_cmd = Twist()
            if hasattr(self, 'cmd_vel_pub'):
                self.cmd_vel_pub.publish(stop_cmd)
            self.log_message("🛑 ACİL DURUM: Robot durduruldu!", "ERROR")
            self.stopped = True
            time.sleep(2)  # Güvenlik için bekle
            
        return py_trees.common.Status.SUCCESS

class UnstickRobot(BaseBehaviorNode):
    """Takılan robotu kurtarma işlemi"""
    
    def __init__(self, name="UnstickRobot"):
        super().__init__(name=name)
        self.attempts = 0
        self.max_attempts = 3
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.cmd_vel_pub = self.node.create_publisher(Twist, 'cmd_vel', 10)
        
    def initialise(self):
        self.attempts = 0
        
    def update(self):
        if self.attempts >= self.max_attempts:
            self.log_message("❌ Robot kurtarılamadı! Manuel müdahale gerekli.", "ERROR")
            return py_trees.common.Status.FAILURE
            
        self.attempts += 1
        self.log_message(f"🔧 Robot kurtarma denemesi {self.attempts}/{self.max_attempts}", "INFO")
        
        # Geri git, dön, ileri git stratejisi
        cmd1 = Twist()
        cmd1.linear.x = -0.1
        cmd1.angular.z = 0.0
        
        cmd2 = Twist()
        cmd2.linear.x = 0.0
        cmd2.angular.z = 0.5
        
        cmd3 = Twist()
        cmd3.linear.x = 0.1
        cmd3.angular.z = 0.0
        
        movements = [(cmd1, 2), (cmd2, 3), (cmd3, 2)]
        
        for movement, duration in movements:
            if hasattr(self, 'cmd_vel_pub'):
                self.cmd_vel_pub.publish(movement)
            time.sleep(duration)
            
        # Durdur
        stop_cmd = Twist()
        if hasattr(self, 'cmd_vel_pub'):
            self.cmd_vel_pub.publish(stop_cmd)
        
        self.log_message("✅ Robot kurtarma tamamlandı!", "INFO")
        return py_trees.common.Status.SUCCESS

class EmptyBin(BaseBehaviorNode):
    """Toz haznesini boşaltma işlemi"""
    
    def __init__(self, name="EmptyBin"):
        super().__init__(name=name)
        self.emptying_time = 0
        self.max_emptying_time = 15
        
    def initialise(self):
        self.emptying_time = 0
        self.log_message("🗑️ Toz haznesi boşaltılıyor...", "INFO")
        
    def update(self):
        self.emptying_time += 1
        
        if self.emptying_time >= self.max_emptying_time:
            self.log_message("✅ Toz haznesi boşaltıldı!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        progress = (self.emptying_time / self.max_emptying_time) * 100
        self.log_message(f"🗑️ Boşaltma ilerlemesi: %{progress:.1f}", "INFO")
        
        return py_trees.common.Status.RUNNING

class FixLocalization(BaseBehaviorNode):
    """Konum hatasını düzeltme işlemi"""
    
    def __init__(self, name="FixLocalization"):
        super().__init__(name=name)
        self.fixing_time = 0
        self.max_fixing_time = 20
        
    def initialise(self):
        self.fixing_time = 0
        self.log_message("📍 Konum hatası düzeltiliyor...", "INFO")
        
    def update(self):
        self.fixing_time += 1
        
        if self.fixing_time >= self.max_fixing_time:
            self.log_message("✅ Konum hatası düzeltildi!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        progress = (self.fixing_time / self.max_fixing_time) * 100
        self.log_message(f"📍 Düzeltme ilerlemesi: %{progress:.1f}", "INFO")
        
        return py_trees.common.Status.RUNNING

class FixSensorError(BaseBehaviorNode):
    """Sensör hatasını düzeltme işlemi"""
    
    def __init__(self, name="FixSensorError"):
        super().__init__(name=name)
        self.fixing_time = 0
        self.max_fixing_time = 10
        
    def initialise(self):
        self.fixing_time = 0
        self.log_message("📡 Sensör hatası düzeltiliyor...", "INFO")
        
    def update(self):
        self.fixing_time += 1
        
        if self.fixing_time >= self.max_fixing_time:
            self.log_message("✅ Sensör hatası düzeltildi!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        progress = (self.fixing_time / self.max_fixing_time) * 100
        self.log_message(f"📡 Düzeltme ilerlemesi: %{progress:.1f}", "INFO")
        
        return py_trees.common.Status.RUNNING

class CoolDown(BaseBehaviorNode):
    """Soğutma işlemi"""
    
    def __init__(self, name="CoolDown"):
        super().__init__(name=name)
        self.cooling_time = 0
        self.max_cooling_time = 30
        
    def initialise(self):
        self.cooling_time = 0
        self.log_message("❄️ Soğutma başladı...", "INFO")
        
    def update(self):
        self.cooling_time += 1
        
        if self.cooling_time >= self.max_cooling_time:
            self.log_message("✅ Soğutma tamamlandı!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        progress = (self.cooling_time / self.max_cooling_time) * 100
        self.log_message(f"❄️ Soğutma ilerlemesi: %{progress:.1f}", "INFO")
        
        return py_trees.common.Status.RUNNING

class GoToDock(BaseBehaviorNode):
    """Şarj istasyonuna gitme işlemi"""
    
    def __init__(self, name="GoToDock"):
        super().__init__(name=name)
        self.dock_found = False
        self.search_time = 0
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.cmd_vel_pub = self.node.create_publisher(Twist, 'cmd_vel', 10)
        
    def initialise(self):
        self.dock_found = False
        self.search_time = 0
        self.log_message("🔋 Şarj istasyonu aranıyor...", "INFO")
        
    def update(self):
        self.search_time += 1
        
        # Simülasyon: 10 saniye sonra dock bulunur
        if self.search_time >= 10:
            self.dock_found = True
            self.log_message("✅ Şarj istasyonu bulundu!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        # Dock arama hareketi
        search_cmd = Twist()
        search_cmd.angular.z = 0.3  # Dönerek ara
        if hasattr(self, 'cmd_vel_pub'):
            self.cmd_vel_pub.publish(search_cmd)
        
        return py_trees.common.Status.RUNNING

class Charge(BaseBehaviorNode):
    """Şarj işlemi"""
    
    def __init__(self, name="Charge", charge_time=30):
        super().__init__(name=name)
        self.charge_time = charge_time
        self.charging_time = 0
        
    def initialise(self):
        self.charging_time = 0
        self.log_message("🔌 Şarj başladı...", "INFO")
        
    def update(self):
        self.charging_time += 1
        
        if self.charging_time >= self.charge_time:
            self.log_message("✅ Şarj tamamlandı! Batarya %100", "INFO")
            return py_trees.common.Status.SUCCESS
            
        progress = (self.charging_time / self.charge_time) * 100
        self.log_message(f"🔌 Şarj devam ediyor... %{progress:.1f}", "INFO")
        
        return py_trees.common.Status.RUNNING

class InitializeSensors(BaseBehaviorNode):
    """Sensörleri başlatma işlemi"""
    
    def __init__(self, name="InitializeSensors"):
        super().__init__(name=name)
        self.sensors_initialized = False
        
    def initialise(self):
        self.sensors_initialized = False
        self.log_message("🔍 Sensörler başlatılıyor...", "INFO")
        
    def update(self):
        if not self.sensors_initialized:
            # Sensör başlatma simülasyonu
            sensors = ['Ultrasonik', 'Infrared', 'Kamera', 'IMU', 'Encoder']
            for sensor in sensors:
                self.log_message(f"  📡 {sensor} sensörü başlatıldı", "INFO")
                time.sleep(0.5)
            
            self.sensors_initialized = True
            self.log_message("✅ Tüm sensörler başlatıldı!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.SUCCESS

class CheckEnvironment(BaseBehaviorNode):
    """Çevre analizi yapar"""
    
    def __init__(self, name="CheckEnvironment"):
        super().__init__(name=name)
        self.environment_checked = False
        
    def initialise(self):
        self.environment_checked = False
        self.log_message("🌍 Çevre analizi yapılıyor...", "INFO")
        
    def update(self):
        if not self.environment_checked:
            # Çevre analizi simülasyonu
            analyses = [
                "Oda boyutu: 5m x 4m",
                "Yüzey tipi: Karışık (halı + parke)",
                "Engel sayısı: 3 adet",
                "Aydınlatma: Yeterli",
                "Sıcaklık: 22°C"
            ]
            
            for analysis in analyses:
                self.log_message(f"  📊 {analysis}", "INFO")
                time.sleep(0.3)
                
            self.environment_checked = True
            self.log_message("✅ Çevre analizi tamamlandı!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.SUCCESS

class SelectCleaningMode(BaseBehaviorNode):
    """Temizlik modunu seçer"""
    
    def __init__(self, name="SelectCleaningMode"):
        super().__init__(name=name)
        self.mode_selected = False
        
    def initialise(self):
        self.mode_selected = False
        self.log_message("🧹 Temizlik modu seçiliyor...", "INFO")
        
    def update(self):
        if not self.mode_selected:
            # Yüzey tipine göre mod seçimi
            surface_types = ['halı', 'parke', 'mermer']
            selected_surface = random.choice(surface_types)
            
            if selected_surface == 'halı':
                mode = "Vakum + Fırça (Güçlü)"
            elif selected_surface == 'parke':
                mode = "Vakum + Islak (Orta)"
            else:
                mode = "Vakum + Kuru (Hassas)"
                
            self.log_message(f"🎯 Seçilen yüzey: {selected_surface}", "INFO")
            self.log_message(f"🧹 Temizlik modu: {mode}", "INFO")
            
            self.mode_selected = True
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.SUCCESS

class ExecuteCleaningPattern(BaseBehaviorNode):
    """Temizlik desenini uygular"""
    
    def __init__(self, name="ExecuteCleaningPattern"):
        super().__init__(name=name)
        self.patterns = ['zigzag', 'spiral', 'grid', 'wall_follow']
        self.current_pattern = None
        self.pattern_time = 0
        self.max_pattern_time = 20
        
    def initialise(self):
        self.current_pattern = random.choice(self.patterns)
        self.pattern_time = 0
        self.log_message(f"🔄 Temizlik deseni: {self.current_pattern}", "INFO")
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.cmd_vel_pub = self.node.create_publisher(Twist, 'cmd_vel', 10)
        
    def update(self):
        self.pattern_time += 1
        
        if self.pattern_time >= self.max_pattern_time:
            self.log_message("✅ Temizlik deseni tamamlandı!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        # Desen bazlı hareket
        cmd = Twist()
        if self.current_pattern == 'zigzag':
            cmd.linear.x = 0.2
            cmd.angular.z = math.sin(self.pattern_time * 0.5) * 0.3
        elif self.current_pattern == 'spiral':
            cmd.linear.x = 0.1
            cmd.angular.z = 0.4
        elif self.current_pattern == 'grid':
            cmd.linear.x = 0.3
            cmd.angular.z = 0.0
        else:  # wall_follow
            cmd.linear.x = 0.2
            cmd.angular.z = 0.2
            
        if hasattr(self, 'cmd_vel_pub'):
            self.cmd_vel_pub.publish(cmd)
        
        progress = (self.pattern_time / self.max_pattern_time) * 100
        self.log_message(f"🔄 {self.current_pattern} deseni: %{progress:.1f}", "INFO")
        
        return py_trees.common.Status.RUNNING

class MonitorCleaningProgress(BaseBehaviorNode):
    """Temizlik ilerlemesini izler"""
    
    def __init__(self, name="MonitorCleaningProgress"):
        super().__init__(name=name)
        self.cleaned_area = 0
        self.total_area = 20  # m²
        self.cleaning_efficiency = 0.85
        
    def update(self):
        # Simülasyon: Her tick'te alan temizlenir
        self.cleaned_area += 0.1 * self.cleaning_efficiency
        
        if self.cleaned_area >= self.total_area:
            self.log_message("✅ Tüm alan temizlendi!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        progress = (self.cleaned_area / self.total_area) * 100
        self.log_message(f"📊 Temizlik ilerlemesi: %{progress:.1f} ({self.cleaned_area:.1f}/{self.total_area} m²)", "INFO")
        
        return py_trees.common.Status.RUNNING

class MonitorBatteryLevel(BaseBehaviorNode):
    """Batarya seviyesini sürekli izler"""
    
    def __init__(self, name="MonitorBatteryLevel"):
        super().__init__(name=name)
        self.current_battery = 100.0
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                BatteryState, 'battery_state', self.battery_callback, 10)
    
    def battery_callback(self, msg):
        self.current_battery = msg.percentage * 100.0
        
    def update(self):
        if self.current_battery < 20:
            self.log_message(f"⚠️ Düşük batarya: %{self.current_battery:.1f}", "WARN")
        elif self.current_battery < 50:
            self.log_message(f"🔋 Batarya: %{self.current_battery:.1f}", "INFO")
        else:
            self.log_message(f"🔋 Batarya: %{self.current_battery:.1f}", "INFO")
            
        return py_trees.common.Status.RUNNING

class MonitorObstacles(BaseBehaviorNode):
    """Engelleri sürekli izler"""
    
    def __init__(self, name="MonitorObstacles"):
        super().__init__(name=name)
        self.obstacle_detected = False
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                Bool, 'obstacle_detected', self.obstacle_callback, 10)
    
    def obstacle_callback(self, msg):
        self.obstacle_detected = msg.data
        
    def update(self):
        if self.obstacle_detected:
            self.log_message("🚧 Engel tespit edildi!", "WARN")
        else:
            self.log_message("✅ Engel yok", "INFO")
            
        return py_trees.common.Status.RUNNING

class MonitorSurfaceType(BaseBehaviorNode):
    """Yüzey tipini izler"""
    
    def __init__(self, name="MonitorSurfaceType"):
        super().__init__(name=name)
        self.surface_types = ['halı', 'parke', 'mermer', 'fayans']
        self.current_surface = 'parke'
        
    def update(self):
        # Simülasyon: Rastgele yüzey değişimi
        if random.random() < 0.1:  # %10 ihtimalle yüzey değişir
            self.current_surface = random.choice(self.surface_types)
            self.log_message(f"🔄 Yüzey değişti: {self.current_surface}", "INFO")
        else:
            self.log_message(f"📋 Mevcut yüzey: {self.current_surface}", "INFO")
            
        return py_trees.common.Status.RUNNING

class MonitorCleaningEfficiency(BaseBehaviorNode):
    """Temizlik verimliliğini izler"""
    
    def __init__(self, name="MonitorCleaningEfficiency"):
        super().__init__(name=name)
        self.efficiency = 0.85
        self.dirt_level = 0.3
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.subscription = self.node.create_subscription(
                Float32, 'dirt_level', self.dirt_callback, 10)
    
    def dirt_callback(self, msg):
        self.dirt_level = msg.data
        
    def update(self):
        # Simülasyon: Verimlilik hesaplama
        if self.dirt_level > 0.5:
            self.efficiency = 0.95  # Çok kirli = yüksek verimlilik
        elif self.dirt_level < 0.1:
            self.efficiency = 0.7   # Az kirli = düşük verimlilik
        else:
            self.efficiency = 0.85  # Normal
            
        self.log_message(f"📈 Temizlik verimliliği: %{self.efficiency*100:.1f}", "INFO")
        return py_trees.common.Status.RUNNING

class ReturnToDock(BaseBehaviorNode):
    """Temizlik sonrası dock'a dönüş"""
    
    def __init__(self, name="ReturnToDock"):
        super().__init__(name=name)
        self.return_time = 0
        self.max_return_time = 8
        
    def setup(self, **kwargs):
        super().setup(**kwargs)
        if self.node:
            self.cmd_vel_pub = self.node.create_publisher(Twist, 'cmd_vel', 10)
        
    def initialise(self):
        self.return_time = 0
        self.log_message("🏠 Dock'a dönüş başladı...", "INFO")
        
    def update(self):
        self.return_time += 1
        
        if self.return_time >= self.max_return_time:
            self.log_message("✅ Dock'a ulaşıldı!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        # Dock'a doğru hareket
        cmd = Twist()
        cmd.linear.x = 0.2
        cmd.angular.z = 0.1
        if hasattr(self, 'cmd_vel_pub'):
            self.cmd_vel_pub.publish(cmd)
        
        progress = (self.return_time / self.max_return_time) * 100
        self.log_message(f"🏠 Dock'a dönüş: %{progress:.1f}", "INFO")
        
        return py_trees.common.Status.RUNNING

class GenerateCleaningReport(BaseBehaviorNode):
    """Temizlik raporu oluşturur"""
    
    def __init__(self, name="GenerateCleaningReport"):
        super().__init__(name=name)
        self.report_generated = False
        
    def initialise(self):
        self.report_generated = False
        self.log_message("📋 Temizlik raporu oluşturuluyor...", "INFO")
        
    def update(self):
        if not self.report_generated:
            # Rapor oluşturma simülasyonu
            report_data = {
                'Temizlik süresi': '45 dakika',
                'Temizlenen alan': '20 m²',
                'Kullanılan enerji': '2.3 kWh',
                'Engel sayısı': '3 adet',
                'Yüzey tipleri': 'Halı, Parke, Mermer',
                'Verimlilik': '%85',
                'Temizlik modu': 'Karışık'
            }
            
            self.log_message("📊 TEMİZLİK RAPORU:", "INFO")
            for key, value in report_data.items():
                self.log_message(f"  {key}: {value}", "INFO")
                
            self.report_generated = True
            self.log_message("✅ Rapor oluşturuldu!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.SUCCESS

class WaitForNextTask(BaseBehaviorNode):
    """Sonraki görev için bekler"""
    
    def __init__(self, name="WaitForNextTask", wait_time=10):
        super().__init__(name=name)
        self.wait_time = wait_time
        self.wait_counter = 0
        
    def initialise(self):
        self.wait_counter = 0
        self.log_message("⏰ Sonraki görev bekleniyor...", "INFO")
        
    def update(self):
        self.wait_counter += 1
        
        if self.wait_counter >= self.wait_time:
            self.log_message("✅ Bekleme tamamlandı, yeni görev başlatılıyor!", "INFO")
            return py_trees.common.Status.SUCCESS
            
        remaining = self.wait_time - self.wait_counter
        self.log_message(f"⏰ Bekleme: {remaining} saniye kaldı", "INFO")
        
        return py_trees.common.Status.RUNNING
