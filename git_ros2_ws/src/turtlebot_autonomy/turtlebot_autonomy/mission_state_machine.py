#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import PoseStamped # PoseStamped de görselleştirebiliriz
from std_msgs.msg import ColorRGBA
from rclpy.duration import Duration

# Waypoint'ler (şimdilik buraya kopyala)
WAYPOINTS = {
    'A': {'x': 0.05, 'y': -0.03, 'z': 0.0, 'w': 1.0},
    'B': {'x': 0.77, 'y': -0.02, 'z': 0.0, 'w': 1.0},
    'C': {'x': 1.97, 'y': -0.04, 'z': 0.0, 'w': 1.0},
    'D': {'x': 2.08, 'y': 0.86, 'z': 0.0, 'w': 1.0}
}

class WaypointPublisherNode(Node):
    def __init__(self):
        super().__init__('simple_waypoint_publisher')
        self.marker_pub = self.create_publisher(MarkerArray, '/waypoint_markers', 10)
        # İstersen PoseStamped de yayınlayabiliriz, ama şimdilik MarkerArray odaklanalım
        # self.pose_pub = self.create_publisher(PoseStamped, '/waypoints_poses', 10) 
        self.timer = self.create_timer(1.0, self.publish_waypoints)
        self.get_logger().info("Simple Waypoint Publisher Node started.")

    def publish_waypoints(self):
        marker_array = MarkerArray()

        for idx, (name, wp) in enumerate(WAYPOINTS.items()):
            marker = Marker()
            marker.header.frame_id = "map"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "waypoints_sphere"
            marker.id = idx
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = wp['x']
            marker.pose.position.y = wp['y']
            marker.pose.orientation.z = wp['z']
            marker.pose.orientation.w = wp['w']
            marker.scale.x = 0.3
            marker.scale.y = 0.3
            marker.scale.z = 0.3
            marker.color = ColorRGBA(r=1.0, g=0.0, b=0.0, a=0.8) # Kırmızı
            marker.lifetime = Duration(seconds=0).to_msg() # Süresiz
            marker_array.markers.append(marker)

            text_marker = Marker()
            text_marker.header = marker.header
            text_marker.ns = "waypoints_labels"
            text_marker.id = idx + 100
            text_marker.type = Marker.TEXT_VIEW_FACING
            text_marker.action = Marker.ADD
            text_marker.pose = marker.pose
            text_marker.pose.position.z += 0.5 
            text_marker.scale.z = 0.3
            text_marker.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0) # Beyaz
            text_marker.text = name
            text_marker.lifetime = Duration(seconds=0).to_msg()
            marker_array.markers.append(text_marker)

        self.marker_pub.publish(marker_array)
        # self.get_logger().info(f"Published MarkerArray with {len(marker_array.markers)} markers.")

def main(args=None):
    rclpy.init(args=args)
    node = WaypointPublisherNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()