import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class CmdVelPublisher(Node):
    def __init__(self):
        super().__init__('cmd_vel_publisher')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer_period = 0.5  # saniye
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.get_logger().info('Cmd Vel Publisher started.')

    def timer_callback(self):
        # Bu düğüm aslında hareket komutları alması gerekir,
        # ancak simülasyon için sadece bir komut yayınlıyoruz.
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing Cmd Vel: linear.x=0.0')

def main(args=None):
    rclpy.init(args=args)
    cmd_vel_publisher = CmdVelPublisher()
    rclpy.spin(cmd_vel_publisher)
    cmd_vel_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()