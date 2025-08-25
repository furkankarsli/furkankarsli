import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
import time

class DistanceSensorPublisher(Node):
    def __init__(self):
        super().__init__('distance_sensor_publisher')
        self.publisher_ = self.create_publisher(Bool, 'obstacle_detected', 10)
        self.timer_period = 5.0  # saniye
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.is_obstacle_detected = False
        self.get_logger().info('Distance Sensor Publisher started.')

    def timer_callback(self):
        msg = Bool()
        # Her 5 saniyede bir engel durumunu değiştir
        self.is_obstacle_detected = not self.is_obstacle_detected
        msg.data = self.is_obstacle_detected
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing Obstacle Detected: {self.is_obstacle_detected}')

def main(args=None):
    rclpy.init(args=args)
    distance_publisher = DistanceSensorPublisher()
    rclpy.spin(distance_publisher)
    distance_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()