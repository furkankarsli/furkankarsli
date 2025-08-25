#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import os
import datetime
import time
from pathlib import Path

class LogManager(Node):
    def __init__(self):
        super().__init__('log_manager')
        
        # Log dizini oluştur
        self.log_dir = Path.home() / "robot_bt_logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Log dosyası adı (tarih ve saat ile)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"robot_bt_session_{timestamp}.log"
        
        # Log dosyasını temizle ve başlat
        self.initialize_log_file()
        
        # Publisher
        self.log_pub = self.create_publisher(String, 'system_log', 10)
        
        # Log mesajlarını dinle
        self.create_subscription(String, 'system_log', self.log_callback, 10)
        
        self.get_logger().info(f"📝 Log Manager başlatıldı: {self.log_file}")
        self.log_message("🚀 ROBOT BT SİSTEMİ BAŞLATILDI", "SYSTEM")
        
    def initialize_log_file(self):
        """Log dosyasını temizle ve başlık ekle"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("🤖 KAPSAMLI TEMİZLİK ROBOTU - SİSTEM LOGU\n")
                f.write("="*80 + "\n")
                f.write(f"📅 Başlangıç Zamanı: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"💻 Sistem: {os.uname().sysname} {os.uname().release}\n")
                f.write(f"👤 Kullanıcı: {os.getenv('USER', 'unknown')}\n")
                f.write("="*80 + "\n\n")
        except Exception as e:
            self.get_logger().error(f"❌ Log dosyası oluşturulamadı: {e}")
    
    def log_message(self, message, level="INFO", source="SYSTEM"):
        """Log mesajını dosyaya ve topic'e yaz"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level:8}] [{source:12}] {message}"
        
        # Dosyaya yaz
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            self.get_logger().error(f"❌ Log dosyasına yazılamadı: {e}")
        
        # Topic'e yayınla
        msg = String()
        msg.data = log_entry
        self.log_pub.publish(msg)
        
        # Console'a da yaz
        if level == "ERROR":
            self.get_logger().error(message)
        elif level == "WARN":
            self.get_logger().warn(message)
        else:
            self.get_logger().info(message)
    
    def log_callback(self, msg):
        """Diğer node'lardan gelen log mesajlarını işle"""
        # Mesajı dosyaya yaz
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(msg.data + "\n")
        except Exception as e:
            self.get_logger().error(f"❌ Log callback hatası: {e}")
    
    def log_system_status(self):
        """Sistem durumunu logla"""
        self.log_message("📊 SİSTEM DURUMU KONTROL EDİLİYOR", "INFO", "SYSTEM")
        
        # Disk kullanımı
        try:
            statvfs = os.statvfs(self.log_dir)
            free_space = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)  # GB
            self.log_message(f"💾 Boş disk alanı: {free_space:.2f} GB", "INFO", "SYSTEM")
        except:
            self.log_message("❌ Disk bilgisi alınamadı", "WARN", "SYSTEM")
        
        # Log dosyası boyutu
        try:
            file_size = self.log_file.stat().st_size / 1024  # KB
            self.log_message(f"📄 Log dosyası boyutu: {file_size:.2f} KB", "INFO", "SYSTEM")
        except:
            self.log_message("❌ Log dosyası bilgisi alınamadı", "WARN", "SYSTEM")

def main(args=None):
    rclpy.init(args=args)
    log_manager = LogManager()
    
    try:
        # Periyodik sistem durumu kontrolü
        log_manager.create_timer(30.0, log_manager.log_system_status)
        rclpy.spin(log_manager)
    except KeyboardInterrupt:
        log_manager.log_message("🛑 Log Manager kapatılıyor...", "INFO", "SYSTEM")
    finally:
        log_manager.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
