import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String
import time
import random
import os
import datetime
from pathlib import Path

class EmergencyPublisher(Node):
    def __init__(self):
        super().__init__('emergency_publisher')
        self.publisher_ = self.create_publisher(Bool, 'emergency_stop', 10)
        self.timer_period = 2.0  # saniye
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.emergency_active = False
        
        # Log dosyası ayarları
        self.log_dir = Path.home() / "robot_bt_logs"
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"robot_bt_session_{timestamp}.log"
        
        self.get_logger().info('🚨 Acil Durum Publisher başlatıldı.')
        self.get_logger().info('💡 Simülasyon: %1 ihtimalle acil durum tetiklenir')
        self.log_message("🚨 Acil durum yayıncısı başlatıldı", "INFO", "EMERGENCY")

    def log_message(self, message, level="INFO", source="EMERGENCY"):
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

    def timer_callback(self):
        msg = Bool()
        
        # Simülasyon: %1 ihtimalle acil durum tetiklenir
        if random.random() < 0.01 and not self.emergency_active:
            self.emergency_active = True
            msg.data = True
            self.log_message("🚨 ACİL DURUM DURDURMA TETİKLENDİ!", "ERROR", "EMERGENCY")
        else:
            msg.data = False
            if self.emergency_active:
                self.emergency_active = False
                self.log_message("✅ Acil durum durdurma iptal edildi", "INFO", "EMERGENCY")
        
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    emergency_publisher = EmergencyPublisher()
    rclpy.spin(emergency_publisher)
    emergency_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
