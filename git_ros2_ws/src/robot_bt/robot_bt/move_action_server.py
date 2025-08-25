import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav2_msgs.action import NavigateToPose
from rclpy.duration import Duration
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

class MoveActionServer(Node):
    def __init__(self):
        super().__init__('move_action_server')
        self._action_server = ActionServer(
            self,
            NavigateToPose,
            'navigate_to_pose',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            handle_accepted_callback=self.handle_accepted_callback,
            cancel_callback=self.cancel_callback
        )
        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            'cmd_vel',
            QoSProfile(
                reliability=ReliabilityPolicy.BEST_EFFORT,
                history=HistoryPolicy.KEEP_LAST,
                depth=1
            )
        )
        self.get_logger().info('MoveActionServer has been started.')

    def goal_callback(self, goal_request):
        self.get_logger().info('Received goal request: "%s"' % goal_request)
        return GoalResponse.ACCEPT

    def handle_accepted_callback(self, goal_handle):
        self.get_logger().info('Goal accepted! Executing...')
        goal_handle.execute()

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received cancel request :(')
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        
        # Simülasyon için 5 saniyelik bir hareket süresi belirleyelim
        move_duration = Duration(seconds=5)
        start_time = self.get_clock().now()
        
        twist = Twist()
        twist.linear.x = 0.2  # İleri doğru 0.2 m/s hızla hareket
        
        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                goal_handle.abort()
                self.get_logger().info('Goal aborted due to cancel request!')
                return NavigateToPose.Result(result=NavigateToPose.Result.CANCELED)

            current_time = self.get_clock().now()
            elapsed_time = current_time - start_time
            
            if elapsed_time >= move_duration:
                break

            # Hareket komutunu yayınla
            self.cmd_vel_publisher.publish(twist)
            self.get_logger().info(f'Moving... Elapsed time: {elapsed_time.nanoseconds / 1e9} s')
            
            rclpy.spin_once(self, timeout_sec=0.1)

        # Hedefe ulaşıldı, hareket durduruluyor
        stop_twist = Twist()
        self.cmd_vel_publisher.publish(stop_twist)
        
        goal_handle.succeed()
        self.get_logger().info('Goal succeeded! Reached the target.')
        return NavigateToPose.Result(result=NavigateToPose.Result.SUCCEEDED)

def main(args=None):
    rclpy.init(args=args)
    action_server = MoveActionServer()
    rclpy.spin(action_server)
    action_server.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()