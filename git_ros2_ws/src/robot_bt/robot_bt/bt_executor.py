import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
import os
import datetime
from pathlib import Path

class RobotCommandProcessor(Node):
    def __init__(self):
        super().__init__('robot_command_processor')
        
        # Log dosyası ayarları
        self.log_dir = Path.home() / "robot_bt_logs"
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"robot_bt_session_{timestamp}.log"
        
        self.get_logger().info('🤖 Kapsamlı Temizlik Robotu Komut İşleyici başlatıldı!')
        self.log_message("🤖 Robot Komut İşleyici başlatıldı", "INFO", "BT_EXECUTOR")
        
        # Robot durumu
        self.robot_state = "IDLE"  # IDLE, CLEANING, DOCKING, CHARGING, PAUSED, ERROR
        self.cleaning_progress = 0
        self.battery_level = 100.0
        
        # Temizlik sekansı için timer
        self.cleaning_timer = None
        self.cleaning_step = 0
        self.is_cleaning = False
        
        # Acil durum kontrolü için subscription
        self.create_subscription(Bool, 'emergency_stop', self.emergency_callback, 10)
        
        # Kullanıcı komutlarını dinle
        self.create_subscription(String, 'user_command', self.user_command_callback, 10)

    def log_message(self, message, level="INFO", source="BT_EXECUTOR"):
        """Log mesajını dosyaya yaz"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level:8}] [{source:12}] {message}"
        
        # Dosyaya yaz
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            self.get_logger().error(f"❌ Log dosyasına yazılamadı: {e}")
        
        # Console'a da yaz
        if level == "ERROR":
            self.get_logger().error(message)
        elif level == "WARN":
            self.get_logger().warn(message)
        else:
            self.get_logger().info(message)

    def start_robot_system(self):
        """Robot sistemini başlat"""
        self.log_message("🚀 Robot sistemi başlatıldı", "INFO", "BT_EXECUTOR")
        
        # Robot durumlarını logla
        self.log_message("🤖 Robot durumları:", "INFO", "BT_EXECUTOR")
        self.log_message("   - Acil durum: PASİF", "INFO", "BT_EXECUTOR")
        self.log_message("   - Takılma: YOK", "INFO", "BT_EXECUTOR")
        self.log_message("   - Batarya: %100", "INFO", "BT_EXECUTOR")
        self.log_message("   - Toz haznesi: BOŞ", "INFO", "BT_EXECUTOR")
        self.log_message("   - Konum hatası: YOK", "INFO", "BT_EXECUTOR")
        self.log_message("   - Sensör hatası: YOK", "INFO", "BT_EXECUTOR")
        self.log_message("   - Aşırı ısınma: YOK", "INFO", "BT_EXECUTOR")
        self.log_message("🔄 Robot şarj istasyonunda bekliyor...", "INFO", "BT_EXECUTOR")

    def spin_tree(self):
        """Robot sistemini çalıştır - sadece kullanıcı komutlarına göre"""
        self.get_logger().info("🚀 Robot sistemi başlatıldı - Kullanıcı komutlarını bekliyor...")
        self.log_message("🚀 Robot sistemi başlatıldı - Kullanıcı komutlarını bekliyor...", "INFO", "BT_EXECUTOR")
        
        # Robot sistemini başlat
        self.start_robot_system()
        
        # Kullanıcı komutlarını dinle
        self.get_logger().info("👂 user_command topic'i dinleniyor...")
        
        try:
            # rclpy.spin() kullanarak callback'lerin çalışmasını sağla
            rclpy.spin(self)
        except KeyboardInterrupt:
            self.get_logger().info("🛑 Robot sistemi durduruldu")
            self.log_message("🛑 Robot sistemi durduruldu", "INFO", "BT_EXECUTOR")
        except Exception as e:
            self.get_logger().error(f"❌ Robot sistemi çalışırken hata: {e}")
            self.log_message(f"❌ Robot sistemi çalışırken hata: {e}", "ERROR", "BT_EXECUTOR")

    def emergency_callback(self, msg):
        """Acil durum mesajını işle"""
        if msg.data:  # Acil durum aktif
            self.log_message("🚨 ACİL DURUM TETİKLENDİ! Tüm işlemler durduruluyor!", "ERROR", "BT_EXECUTOR")
            self.get_logger().error("🚨 ACİL DURUM TETİKLENDİ! Tüm işlemler durduruluyor!")
            
            # Temizlik varsa durdur
            if self.is_cleaning:
                self.log_message("🛑 Temizlik acil durum nedeniyle durduruldu!", "ERROR", "BT_EXECUTOR")
                self.get_logger().error("🛑 Temizlik acil durum nedeniyle durduruldu!")
                
                # Timer'ı durdur ve temizlik durumunu sıfırla
                if self.cleaning_timer:
                    self.cleaning_timer.cancel()
                    self.cleaning_timer = None
                
                self.is_cleaning = False
                self.robot_state = "ERROR"
        else:  # Acil durum pasif
            self.log_message("✅ Acil durum kaldırıldı", "INFO", "BT_EXECUTOR")
            self.get_logger().info("✅ Acil durum kaldırıldı")
            if self.robot_state == "ERROR":
                self.robot_state = "IDLE"

    def check_emergency_conditions(self):
        """Sadece acil durumları kontrol et"""
        # Acil durum, takılma, kritik batarya gibi durumları kontrol et
        # Ama otomatik temizlik başlatma
        pass

    def user_command_callback(self, msg):
        """Kullanıcı komutlarını işle"""
        try:
            command = msg.data
            self.get_logger().info(f"🎯 CALLBACK ÇALIŞTI! Komut: {command}")
            self.log_message(f"📨 Kullanıcı komutu alındı: {command}", "INFO", "BT_EXECUTOR")
            
            if command == "START_CLEANING":
                self.get_logger().info("🧹 START_CLEANING komutu işleniyor...")
                self.execute_cleaning_sequence()
            elif command == "GO_TO_DOCK":
                self.get_logger().info("🔋 GO_TO_DOCK komutu işleniyor...")
                self.execute_docking_sequence()
            elif command == "PAUSE":
                self.get_logger().info("⏸️ PAUSE komutu işleniyor...")
                self.pause_robot()
            elif command == "RESUME":
                self.get_logger().info("▶️ RESUME komutu işleniyor...")
                self.resume_robot()
            elif command == "STOP":
                self.get_logger().info("🛑 STOP komutu işleniyor...")
                self.stop_robot()
            elif command == "RESET":
                self.get_logger().info("🔄 RESET komutu işleniyor...")
                self.reset_robot()
            else:
                self.log_message(f"❌ Bilinmeyen komut: {command}", "WARN", "BT_EXECUTOR")
                self.get_logger().warn(f"❌ Bilinmeyen komut: {command}")
        except Exception as e:
            self.get_logger().error(f"❌ Callback hatası: {e}")
            self.log_message(f"❌ Callback hatası: {e}", "ERROR", "BT_EXECUTOR")

    def execute_cleaning_sequence(self):
        """Temizlik sekansını çalıştır"""
        if self.is_cleaning:
            self.get_logger().warn("🧹 Temizlik zaten devam ediyor!")
            return
            
        if self.robot_state == "ERROR":
            self.get_logger().warn("🚨 Acil durum nedeniyle temizlik başlatılamıyor!")
            return
            
        self.log_message("🧹 Temizlik sekansı başlatılıyor...", "INFO", "BT_EXECUTOR")
        self.get_logger().info("🧹 Temizlik sekansı başlatılıyor...")
        
        # Temizlik durumunu başlat
        self.is_cleaning = True
        self.cleaning_step = 0
        self.robot_state = "CLEANING"
        
        # Başlangıç kontrolleri
        self.log_message("🔍 Başlangıç kontrolleri yapılıyor...", "INFO", "BT_EXECUTOR")
        self.get_logger().info("🔍 Başlangıç kontrolleri yapılıyor...")
        
        # Timer ile temizlik sekansını başlat
        self.cleaning_timer = self.create_timer(2.0, self.cleaning_step_callback)
        
    def cleaning_step_callback(self):
        """Temizlik adımlarını işle"""
        if not self.is_cleaning or self.robot_state == "PAUSED" or self.robot_state == "ERROR":
            return
            
        self.cleaning_step += 1
        
        if self.cleaning_step == 1:
            # Temizlik modu seçimi
            self.log_message("🎯 Temizlik modu seçiliyor...", "INFO", "BT_EXECUTOR")
            self.get_logger().info("🎯 Temizlik modu seçiliyor...")
            self.cleaning_timer.cancel()
            self.cleaning_timer = self.create_timer(1.0, self.cleaning_step_callback)
            
        elif self.cleaning_step == 2:
            # Temizlik deseni başlat
            self.log_message("🔄 Temizlik deseni çalıştırılıyor...", "INFO", "BT_EXECUTOR")
            self.get_logger().info("🔄 Temizlik deseni çalıştırılıyor...")
            self.cleaning_timer.cancel()
            self.cleaning_timer = self.create_timer(1.0, self.cleaning_progress_callback)
            
    def cleaning_progress_callback(self):
        """Temizlik ilerlemesini işle"""
        if not self.is_cleaning or self.robot_state == "PAUSED":
            return
            
        progress = (self.cleaning_step - 1) * 5  # Her adımda %5 ilerleme
        self.log_message(f"🧹 Temizlik ilerlemesi: %{progress}", "INFO", "BT_EXECUTOR")
        self.get_logger().info(f"🧹 Temizlik ilerlemesi: %{progress}")
        
        self.cleaning_step += 1
        
        if self.cleaning_step > 22:  # 20 adım + 2 başlangıç adımı
            # Temizlik tamamlandı
            self.log_message("✅ Temizlik tamamlandı!", "INFO", "BT_EXECUTOR")
            self.get_logger().info("✅ Temizlik tamamlandı!")
            
            # Şarj istasyonuna git
            self.log_message("🔋 Şarj istasyonuna gidiliyor...", "INFO", "BT_EXECUTOR")
            self.get_logger().info("🔋 Şarj istasyonuna gidiliyor...")
            
            self.cleaning_timer.cancel()
            self.cleaning_timer = self.create_timer(3.0, self.docking_complete_callback)
            
    def docking_complete_callback(self):
        """Şarj istasyonuna ulaşma tamamlandı"""
        self.log_message("✅ Şarj istasyonuna ulaşıldı!", "INFO", "BT_EXECUTOR")
        self.get_logger().info("✅ Şarj istasyonuna ulaşıldı!")
        
        # Temizlik durumunu sıfırla
        self.is_cleaning = False
        self.robot_state = "IDLE"
        self.cleaning_timer.cancel()
        self.cleaning_timer = None

    def execute_docking_sequence(self):
        """Şarj istasyonuna gitme sekansını çalıştır"""
        self.log_message("🔋 Şarj istasyonuna gidiliyor...", "INFO", "BT_EXECUTOR")
        
        try:
            # Konum belirleme
            self.log_message("📍 Konum belirleniyor...", "INFO", "BT_EXECUTOR")
            time.sleep(1)
            
            # Şarj istasyonuna gitme
            self.log_message("🚶 Şarj istasyonuna hareket ediliyor...", "INFO", "BT_EXECUTOR")
            time.sleep(3)
            
            # Şarj başlatma
            self.log_message("🔌 Şarj başlatılıyor...", "INFO", "BT_EXECUTOR")
            time.sleep(2)
            
            self.log_message("✅ Şarj istasyonuna ulaşıldı ve şarj başladı!", "INFO", "BT_EXECUTOR")
            
        except Exception as e:
            self.log_message(f"❌ Şarj istasyonuna gitme sırasında hata: {e}", "ERROR", "BT_EXECUTOR")

    def pause_robot(self):
        """Robotu duraklat"""
        if self.is_cleaning:
            self.log_message("⏸️ Temizlik duraklatıldı", "INFO", "BT_EXECUTOR")
            self.get_logger().info("⏸️ Temizlik duraklatıldı")
            
            # Timer'ı durdur
            if self.cleaning_timer:
                self.cleaning_timer.cancel()
                self.cleaning_timer = None
            
            self.robot_state = "PAUSED"
        else:
            self.log_message("⏸️ Robot duraklatıldı", "INFO", "BT_EXECUTOR")
            self.get_logger().info("⏸️ Robot duraklatıldı")

    def resume_robot(self):
        """Robotu devam ettir"""
        if self.robot_state == "PAUSED" and self.is_cleaning:
            self.log_message("▶️ Temizlik devam ettiriliyor", "INFO", "BT_EXECUTOR")
            self.get_logger().info("▶️ Temizlik devam ettiriliyor")
            
            # Timer'ı yeniden başlat
            self.cleaning_timer = self.create_timer(1.0, self.cleaning_progress_callback)
            self.robot_state = "CLEANING"
        else:
            self.log_message("▶️ Robot devam ettiriliyor", "INFO", "BT_EXECUTOR")
            self.get_logger().info("▶️ Robot devam ettiriliyor")

    def stop_robot(self):
        """Robotu durdur"""
        if self.is_cleaning:
            self.log_message("🛑 Temizlik durduruldu", "INFO", "BT_EXECUTOR")
            self.get_logger().info("🛑 Temizlik durduruldu")
            
            # Timer'ı durdur ve temizlik durumunu sıfırla
            if self.cleaning_timer:
                self.cleaning_timer.cancel()
                self.cleaning_timer = None
            
            self.is_cleaning = False
            self.robot_state = "IDLE"
        else:
            self.log_message("🛑 Robot durduruldu", "INFO", "BT_EXECUTOR")
            self.get_logger().info("🛑 Robot durduruldu")

    def reset_robot(self):
        """Robotu sıfırla"""
        self.log_message("🔄 Robot sıfırlanıyor...", "INFO", "BT_EXECUTOR")
        time.sleep(2)
        self.log_message("✅ Robot sıfırlandı!", "INFO", "BT_EXECUTOR")

def main(args=None):
    rclpy.init(args=args)
    
    processor = RobotCommandProcessor()
    processor.spin_tree()
    
    processor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()