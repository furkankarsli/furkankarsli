#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time

class TestBehaviorTree(Node):
    def __init__(self):
        super().__init__('test_behavior_tree')
        self.publisher = self.create_publisher(String, '/robot_command', 10)
        self.get_logger().info('Test node başlatıldı. Komutlar gönderiliyor...')
        
    def send_command(self, command):
        msg = String()
        msg.data = command
        self.publisher.publish(msg)
        self.get_logger().info(f'Komut gönderildi: {command}')
        
    def test_sequence(self):
        """Test sırası: task1 -> task2 -> task3"""
        commands = ['task1', 'task2', 'task3']
        
        for cmd in commands:
            self.send_command(cmd)
            self.get_logger().info(f'{cmd} komutu gönderildi, 15 saniye bekleniyor...')
            time.sleep(15)
            
        self.get_logger().info('Test tamamlandı!')

def main(args=None):
    rclpy.init(args=args)
    test_node = TestBehaviorTree()
    
    try:
        # Test sırasını başlat
        test_node.test_sequence()
    except KeyboardInterrupt:
        test_node.get_logger().info('Test kesildi.')
    finally:
        test_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
