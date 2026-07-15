from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='agv_autonomy',
            executable='agv_behavior_tree',
            name='agv_behavior_tree',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )
    ])
