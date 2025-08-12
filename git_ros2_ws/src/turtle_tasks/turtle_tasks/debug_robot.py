#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformListener, Buffer
import time

class RobotDebugger(Node):
    def __init__(self):
        super().__init__('robot_debugger')
        
        # Nav2 action client
        self.nav2_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        
        # Robot pozisyonu için subscriber
        self.odom_sub = self.create_subscription(
            Odometry, 
            '/odom', 
            self.odom_callback, 
            10
        )
        
        # Robot hızı için subscriber
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # TF listener
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        self.robot_position = None
        self.robot_velocity = None
        
        self.get_logger().info('Robot Debugger başlatıldı')
        
    def odom_callback(self, msg):
        self.robot_position = msg.pose.pose
        self.robot_velocity = msg.twist.twist
        
    def cmd_vel_callback(self, msg):
        self.get_logger().info(f'Robot hızı: linear={msg.linear}, angular={msg.angular}')
        
    def check_nav2_status(self):
        self.get_logger().info('=== Nav2 Durumu Kontrol Ediliyor ===')
        
        # Action server kontrolü
        if self.nav2_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().info('✅ Nav2 action server çalışıyor')
        else:
            self.get_logger().error('❌ Nav2 action server bulunamadı!')
            return False
            
        # Topic kontrolü
        topics = self.get_topic_names_and_types()
        nav2_topics = [topic for topic, types in topics if 'nav2' in topic or 'navigate' in topic]
        
        if nav2_topics:
            self.get_logger().info(f'✅ Nav2 topic\'leri bulundu: {nav2_topics}')
        else:
            self.get_logger().warning('⚠️ Nav2 topic\'leri bulunamadı')
            
        return True
        
    def check_robot_status(self):
        self.get_logger().info('=== Robot Durumu Kontrol Ediliyor ===')
        
        # Pozisyon kontrolü
        if self.robot_position:
            pos = self.robot_position.position
            orient = self.robot_position.orientation
            self.get_logger().info(f'✅ Robot pozisyonu: x={pos.x:.2f}, y={pos.y:.2f}, z={pos.z:.2f}')
            self.get_logger().info(f'✅ Robot yönelimi: x={orient.x:.2f}, y={orient.y:.2f}, z={orient.z:.2f}, w={orient.w:.2f}')
        else:
            self.get_logger().warning('⚠️ Robot pozisyonu henüz alınamadı')
            
        # Hız kontrolü
        if self.robot_velocity:
            linear = self.robot_velocity.linear
            angular = self.robot_velocity.angular
            self.get_logger().info(f'✅ Robot hızı: linear=({linear.x:.2f}, {linear.y:.2f}, {linear.z:.2f})')
            self.get_logger().info(f'✅ Robot açısal hızı: ({angular.x:.2f}, {angular.y:.2f}, {angular.z:.2f})')
        else:
            self.get_logger().warning('⚠️ Robot hızı henüz alınamadı')
            
    def check_tf_status(self):
        self.get_logger().info('=== TF Durumu Kontrol Ediliyor ===')
        
        try:
            # map -> base_link transform kontrolü
            transform = self.tf_buffer.lookup_transform(
                'map', 'base_link', rclpy.time.Time()
            )
            self.get_logger().info('✅ map -> base_link transform bulundu')
            self.get_logger().info(f'   Pozisyon: x={transform.transform.translation.x:.2f}, y={transform.transform.translation.y:.2f}')
        except Exception as e:
            self.get_logger().warning(f'⚠️ map -> base_link transform bulunamadı: {e}')
            
    def run_diagnostics(self):
        self.get_logger().info('Robot durumu teşhisi başlatılıyor...')
        
        # Nav2 kontrolü
        nav2_ok = self.check_nav2_status()
        
        # Robot durumu kontrolü
        self.check_robot_status()
        
        # TF kontrolü
        self.check_tf_status()
        
        if nav2_ok:
            self.get_logger().info('🎉 Nav2 çalışıyor! Robot hareket edebilir.')
        else:
            self.get_logger().error('💥 Nav2 çalışmıyor! Robot hareket edemez.')
            
        return nav2_ok

def main(args=None):
    rclpy.init(args=args)
    debugger = RobotDebugger()
    
    try:
        # Biraz bekle ki topic'lerden veri gelsin
        time.sleep(2)
        
        # Teşhisi çalıştır
        debugger.run_diagnostics()
        
        # Sürekli çalış
        rclpy.spin(debugger)
        
    except KeyboardInterrupt:
        pass
    finally:
        debugger.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
