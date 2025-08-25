#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String, Int32, Float32
from sensor_msgs.msg import BatteryState
from geometry_msgs.msg import PoseStamped
from std_srvs.srv import Trigger
import time
import threading
import sys
import os
import datetime
from pathlib import Path

class UserCommandInterface(Node):
    def __init__(self):
        super().__init__('user_command_interface')
        
        # Publishers
        self.emergency_pub = self.create_publisher(Bool, 'emergency_stop', 10)
        self.obstacle_pub = self.create_publisher(Bool, 'obstacle_detected', 10)
        self.battery_pub = self.create_publisher(BatteryState, 'battery_state', 10)
        self.bin_state_pub = self.create_publisher(Bool, 'bin_state', 10)
        self.tangled_pub = self.create_publisher(Bool, 'tangled_state', 10)
        self.dirt_level_pub = self.create_publisher(Float32, 'dirt_level', 10)
        self.localization_error_pub = self.create_publisher(Bool, 'localization_error', 10)
        self.sensor_status_pub = self.create_publisher(String, 'sensor_status', 10)
        self.temperature_pub = self.create_publisher(Float32, 'temperature_status', 10)
        self.user_command_pub = self.create_publisher(String, 'user_command', 10)
        
        # Log dosyası ayarları
        self.log_dir = Path.home() / "robot_bt_logs"
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"robot_bt_session_{timestamp}.log"
        
        # Service clients
        self.clean_service_client = self.create_client(Trigger, 'clean_area')
        self.move_service_client = self.create_client(Trigger, 'navigate_to_pose')
        
        # Current robot state
        self.current_battery = 100.0
        self.current_dirt_level = 0.3
        self.current_temperature = 25.0
        self.is_emergency = False
        self.is_obstacle = False
        self.is_bin_full = False
        self.is_tangled = False
        self.is_localization_error = False
        self.sensor_status = "OK"
        
        # Start command interface
        self.get_logger().info("🎮 Kullanıcı Komut Arayüzü başlatıldı!")
        self.get_logger().info("📋 Kullanılabilir komutlar için 'help' yazın")
        self.log_message("🎮 Kullanıcı komut arayüzü başlatıldı", "INFO", "USER_CMD")
        
        # Show initial help
        self.show_help()
        
        # Start command timer
        self.create_timer(0.1, self.check_for_commands)
        
    def log_message(self, message, level="INFO", source="USER_CMD"):
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
        
    def check_for_commands(self):
        """Komut kontrolü için timer callback"""
        try:
            if sys.stdin.isatty():
                command = input("\n🤖 Robot Komutu: ").strip().lower()
                self.process_command(command)
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Komut arayüzü kapatılıyor...")
            try:
                rclpy.shutdown()
            except RuntimeError:
                pass
        except Exception as e:
            print(f"❌ Komut hatası: {e}")
    
    def process_command(self, command):
        """Komutları işler"""
        if command == 'help' or command == 'h':
            self.show_help()
        elif command == 'status':
            self.show_status()
        elif command.startswith('battery'):
            self.set_battery(command)
        elif command.startswith('obstacle'):
            self.set_obstacle(command)
        elif command.startswith('emergency'):
            self.set_emergency(command)
        elif command.startswith('dirt'):
            self.set_dirt_level(command)
        elif command.startswith('temperature'):
            self.set_temperature(command)
        elif command.startswith('bin'):
            self.set_bin_state(command)
        elif command.startswith('tangled'):
            self.set_tangled(command)
        elif command.startswith('localization'):
            self.set_localization_error(command)
        elif command.startswith('sensor'):
            self.set_sensor_status(command)
        elif command == 'clean':
            self.start_cleaning()
        elif command == 'dock':
            self.go_to_dock()
        elif command == 'pause':
            self.pause_robot()
        elif command == 'resume':
            self.resume_robot()
        elif command == 'stop':
            self.stop_robot()
        elif command == 'reset':
            self.reset_robot()
        elif command == 'quit' or command == 'q':
            print("👋 Robot komut arayüzü kapatılıyor...")
            rclpy.shutdown()
        elif command == '':
            pass  # Boş komut, hiçbir şey yapma
        else:
            print(f"❌ Bilinmeyen komut: {command}")
            print("💡 Yardım için 'help' yazın")
    
    def show_help(self):
        """Yardım menüsünü gösterir"""
        print("\n" + "="*60)
        print("🤖 KAPSAMLI TEMİZLİK ROBOTU - KOMUT ARAYÜZÜ")
        print("="*60)
        print("\n📋 DURUM KONTROL KOMUTLARI:")
        print("  status                    - Mevcut robot durumunu göster")
        print("  battery <0-100>           - Batarya seviyesini ayarla")
        print("  obstacle <on/off>         - Engel durumunu ayarla")
        print("  emergency <on/off>        - Acil durum butonunu ayarla")
        print("  dirt <0.0-1.0>            - Kir seviyesini ayarla")
        print("  temperature <0-100>       - Sıcaklığı ayarla")
        print("  bin <full/empty>          - Toz haznesi durumunu ayarla")
        print("  tangled <on/off>          - Fırça/tekerlek takılma durumu")
        print("  localization <on/off>     - Konum kaybı durumu")
        print("  sensor <status>           - Sensör durumunu ayarla")
        print("\n🎯 GÖREV KOMUTLARI:")
        print("  clean                     - Temizlik görevini başlat")
        print("  dock                      - Şarj istasyonuna git")
        print("  pause                     - Robotu duraklat")
        print("  resume                    - Robotu devam ettir")
        print("  stop                      - Robotu durdur")
        print("  reset                     - Robotu sıfırla")
        print("\n🔧 SİSTEM KOMUTLARI:")
        print("  help (h)                  - Bu yardım menüsünü göster")
        print("  quit (q)                  - Programı kapat")
        print("\n" + "="*60)
    
    def show_status(self):
        """Mevcut robot durumunu gösterir"""
        print("\n" + "="*50)
        print("📊 ROBOT DURUM RAPORU")
        print("="*50)
        print(f"🔋 Batarya: %{self.current_battery:.1f}")
        print(f"🌡️ Sıcaklık: {self.current_temperature:.1f}°C")
        print(f"🧹 Kir Seviyesi: {self.current_dirt_level:.2f}")
        print(f"🚨 Acil Durum: {'AKTİF' if self.is_emergency else 'PASİF'}")
        print(f"🚧 Engel: {'VAR' if self.is_obstacle else 'YOK'}")
        print(f"🗑️ Toz Haznesi: {'DOLU' if self.is_bin_full else 'BOŞ'}")
        print(f"🔗 Takılma: {'VAR' if self.is_tangled else 'YOK'}")
        print(f"📍 Konum Hatası: {'VAR' if self.is_localization_error else 'YOK'}")
        print(f"📡 Sensör Durumu: {self.sensor_status}")
        print("="*50)
    
    def set_battery(self, command):
        """Batarya seviyesini ayarlar"""
        try:
            parts = command.split()
            if len(parts) == 2:
                level = float(parts[1])
                if 0 <= level <= 100:
                    self.current_battery = level
                    self.publish_battery()
                    self.log_message(f"🔋 Batarya seviyesi %{level:.1f} olarak ayarlandı", "INFO", "USER_CMD")
                    print(f"✅ Batarya seviyesi %{level:.1f} olarak ayarlandı")
                else:
                    self.log_message("❌ Geçersiz batarya seviyesi (0-100 arası olmalı)", "WARN", "USER_CMD")
                    print("❌ Batarya seviyesi 0-100 arasında olmalı")
            else:
                print("❌ Kullanım: battery <0-100>")
        except ValueError:
            self.log_message("❌ Geçersiz batarya seviyesi formatı", "ERROR", "USER_CMD")
            print("❌ Geçersiz batarya seviyesi")
    
    def set_obstacle(self, command):
        """Engel durumunu ayarlar"""
        parts = command.split()
        if len(parts) == 2:
            if parts[1] in ['on', 'true', '1']:
                self.is_obstacle = True
                print("✅ Engel durumu: VAR")
            elif parts[1] in ['off', 'false', '0']:
                self.is_obstacle = False
                print("✅ Engel durumu: YOK")
            else:
                print("❌ Kullanım: obstacle <on/off>")
        else:
            print("❌ Kullanım: obstacle <on/off>")
        self.publish_obstacle()
    
    def set_emergency(self, command):
        """Acil durum durumunu ayarlar"""
        parts = command.split()
        if len(parts) == 2:
            if parts[1] in ['on', 'true', '1']:
                self.is_emergency = True
                print("🚨 ACİL DURUM AKTİF!")
            elif parts[1] in ['off', 'false', '0']:
                self.is_emergency = False
                print("✅ Acil durum iptal edildi")
            else:
                print("❌ Kullanım: emergency <on/off>")
        else:
            print("❌ Kullanım: emergency <on/off>")
        self.publish_emergency()
    
    def set_dirt_level(self, command):
        """Kir seviyesini ayarlar"""
        try:
            parts = command.split()
            if len(parts) == 2:
                level = float(parts[1])
                if 0 <= level <= 1:
                    self.current_dirt_level = level
                    self.publish_dirt_level()
                    print(f"✅ Kir seviyesi {level:.2f} olarak ayarlandı")
                else:
                    print("❌ Kir seviyesi 0.0-1.0 arasında olmalı")
            else:
                print("❌ Kullanım: dirt <0.0-1.0>")
        except ValueError:
            print("❌ Geçersiz kir seviyesi")
    
    def set_temperature(self, command):
        """Sıcaklığı ayarlar"""
        try:
            parts = command.split()
            if len(parts) == 2:
                temp = float(parts[1])
                if 0 <= temp <= 100:
                    self.current_temperature = temp
                    self.publish_temperature()
                    print(f"✅ Sıcaklık {temp:.1f}°C olarak ayarlandı")
                else:
                    print("❌ Sıcaklık 0-100°C arasında olmalı")
            else:
                print("❌ Kullanım: temperature <0-100>")
        except ValueError:
            print("❌ Geçersiz sıcaklık değeri")
    
    def set_bin_state(self, command):
        """Toz haznesi durumunu ayarlar"""
        parts = command.split()
        if len(parts) == 2:
            if parts[1] in ['full', 'dolu']:
                self.is_bin_full = True
                print("✅ Toz haznesi: DOLU")
            elif parts[1] in ['empty', 'boş']:
                self.is_bin_full = False
                print("✅ Toz haznesi: BOŞ")
            else:
                print("❌ Kullanım: bin <full/empty>")
        else:
            print("❌ Kullanım: bin <full/empty>")
        self.publish_bin_state()
    
    def set_tangled(self, command):
        """Takılma durumunu ayarlar"""
        parts = command.split()
        if len(parts) == 2:
            if parts[1] in ['on', 'true', '1']:
                self.is_tangled = True
                print("✅ Takılma durumu: VAR")
            elif parts[1] in ['off', 'false', '0']:
                self.is_tangled = False
                print("✅ Takılma durumu: YOK")
            else:
                print("❌ Kullanım: tangled <on/off>")
        else:
            print("❌ Kullanım: tangled <on/off>")
        self.publish_tangled()
    
    def set_localization_error(self, command):
        """Konum hatası durumunu ayarlar"""
        parts = command.split()
        if len(parts) == 2:
            if parts[1] in ['on', 'true', '1']:
                self.is_localization_error = True
                print("✅ Konum hatası: VAR")
            elif parts[1] in ['off', 'false', '0']:
                self.is_localization_error = False
                print("✅ Konum hatası: YOK")
            else:
                print("❌ Kullanım: localization <on/off>")
        else:
            print("❌ Kullanım: localization <on/off>")
        self.publish_localization_error()
    
    def set_sensor_status(self, command):
        """Sensör durumunu ayarlar"""
        parts = command.split()
        if len(parts) >= 2:
            status = ' '.join(parts[1:])
            self.sensor_status = status
            self.publish_sensor_status()
            print(f"✅ Sensör durumu: {status}")
        else:
            print("❌ Kullanım: sensor <status>")
    
    def start_cleaning(self):
        """Temizlik görevini başlatır"""
        self.log_message("🧹 Temizlik görevi başlatılıyor...", "INFO", "USER_CMD")
        print("🧹 Temizlik görevi başlatılıyor...")
        self.send_user_command("START_CLEANING")
    
    def go_to_dock(self):
        """Şarj istasyonuna gitme görevini başlatır"""
        self.log_message("🔋 Şarj istasyonuna gidiliyor...", "INFO", "USER_CMD")
        print("🔋 Şarj istasyonuna gidiliyor...")
        self.send_user_command("GO_TO_DOCK")
    
    def pause_robot(self):
        """Robotu duraklatır"""
        self.log_message("⏸️ Robot duraklatılıyor...", "INFO", "USER_CMD")
        print("⏸️ Robot duraklatılıyor...")
        self.send_user_command("PAUSE")
    
    def resume_robot(self):
        """Robotu devam ettirir"""
        self.log_message("▶️ Robot devam ettiriliyor...", "INFO", "USER_CMD")
        print("▶️ Robot devam ettiriliyor...")
        self.send_user_command("RESUME")
    
    def stop_robot(self):
        """Robotu durdurur"""
        self.log_message("🛑 Robot durduruluyor...", "INFO", "USER_CMD")
        print("🛑 Robot durduruluyor...")
        self.send_user_command("STOP")
    
    def reset_robot(self):
        """Robotu sıfırlar"""
        self.log_message("🔄 Robot sıfırlanıyor...", "INFO", "USER_CMD")
        print("🔄 Robot sıfırlanıyor...")
        self.current_battery = 100.0
        self.current_dirt_level = 0.3
        self.current_temperature = 25.0
        self.is_emergency = False
        self.is_obstacle = False
        self.is_bin_full = False
        self.is_tangled = False
        self.is_localization_error = False
        self.sensor_status = "OK"
        
        # Tüm durumları yayınla
        self.publish_all_states()
        self.log_message("✅ Robot durumları sıfırlandı", "INFO", "USER_CMD")
        print("✅ Robot durumları sıfırlandı")
    
    def send_user_command(self, command):
        """Kullanıcı komutunu yayınlar"""
        msg = String()
        msg.data = command
        self.user_command_pub.publish(msg)
    
    def publish_battery(self):
        """Batarya durumunu yayınlar"""
        msg = BatteryState()
        msg.percentage = self.current_battery / 100.0
        msg.voltage = 12.0 + (self.current_battery / 100.0) * 2.0
        self.battery_pub.publish(msg)
    
    def publish_obstacle(self):
        """Engel durumunu yayınlar"""
        msg = Bool()
        msg.data = self.is_obstacle
        self.obstacle_pub.publish(msg)
    
    def publish_emergency(self):
        """Acil durum durumunu yayınlar"""
        msg = Bool()
        msg.data = self.is_emergency
        self.emergency_pub.publish(msg)
    
    def publish_dirt_level(self):
        """Kir seviyesini yayınlar"""
        msg = Float32()
        msg.data = self.current_dirt_level
        self.dirt_level_pub.publish(msg)
    
    def publish_temperature(self):
        """Sıcaklığı yayınlar"""
        msg = Float32()
        msg.data = self.current_temperature
        self.temperature_pub.publish(msg)
    
    def publish_bin_state(self):
        """Toz haznesi durumunu yayınlar"""
        msg = Bool()
        msg.data = self.is_bin_full
        self.bin_state_pub.publish(msg)
    
    def publish_tangled(self):
        """Takılma durumunu yayınlar"""
        msg = Bool()
        msg.data = self.is_tangled
        self.tangled_pub.publish(msg)
    
    def publish_localization_error(self):
        """Konum hatası durumunu yayınlar"""
        msg = Bool()
        msg.data = self.is_localization_error
        self.localization_error_pub.publish(msg)
    
    def publish_sensor_status(self):
        """Sensör durumunu yayınlar"""
        msg = String()
        msg.data = self.sensor_status
        self.sensor_status_pub.publish(msg)
    
    def publish_all_states(self):
        """Tüm durumları yayınlar"""
        self.publish_battery()
        self.publish_obstacle()
        self.publish_emergency()
        self.publish_dirt_level()
        self.publish_temperature()
        self.publish_bin_state()
        self.publish_tangled()
        self.publish_localization_error()
        self.publish_sensor_status()

def main(args=None):
    rclpy.init(args=args)
    interface = UserCommandInterface()
    
    try:
        rclpy.spin(interface)
    except KeyboardInterrupt:
        print("\n👋 Kullanıcı arayüzü kapatılıyor...")
    finally:
        interface.destroy_node()
        try:
            rclpy.shutdown()
        except RuntimeError:
            pass  # Context zaten kapatılmış olabilir

if __name__ == '__main__':
    main()
