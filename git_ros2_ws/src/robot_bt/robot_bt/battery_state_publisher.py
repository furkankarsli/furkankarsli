import rclpy
from rclpy.node import Node
from sensor_msgs.msg import BatteryState
from std_msgs.msg import String
import time
import os
import datetime
from pathlib import Path

class BatteryStatePublisher(Node):
    def __init__(self):
        super().__init__('battery_state_publisher')
        self.publisher_ = self.create_publisher(BatteryState, 'battery_state', 10)
        self.timer_period = 1.0  # saniye
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.current_battery_level = 100.0
        
        # Log dosyası ayarları
        self.log_dir = Path.home() / "robot_bt_logs"
        self.log_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"robot_bt_session_{timestamp}.log"
        
        # İlk log mesajı
        self.log_message("🔋 Battery State Publisher başlatıldı", "INFO", "BATTERY")
        self.get_logger().info('🔋 Battery State Publisher başlatıldı.')

    def log_message(self, message, level="INFO", source="BATTERY"):
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
        msg = BatteryState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.percentage = float(self.current_battery_level / 100.0)
        self.publisher_.publish(msg)
        
        # Log mesajı
        if self.current_battery_level <= 15.0:
            self.log_message(f"🔋 KRİTİK BATARYA: {self.current_battery_level:.1f}%", "ERROR", "BATTERY")
        elif self.current_battery_level <= 30.0:
            self.log_message(f"🔋 Düşük batarya: {self.current_battery_level:.1f}%", "WARN", "BATTERY")
        else:
            self.log_message(f"🔋 Batarya seviyesi: {self.current_battery_level:.1f}%", "INFO", "BATTERY")

        # Batarya seviyesini düşür
        self.current_battery_level -= 0.5 
        if self.current_battery_level < 0.0:
            self.current_battery_level = 100.0  # Şarj olduğunu simüle et
            self.log_message("🔋 Batarya şarj edildi: %100", "INFO", "BATTERY")

def main(args=None):
    rclpy.init(args=args)
    battery_publisher = BatteryStatePublisher()
    rclpy.spin(battery_publisher)
    battery_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()