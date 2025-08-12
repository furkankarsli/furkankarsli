#!/usr/bin/env python3

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        # Behavior tree node
        Node(
            package='turtle_tasks',
            executable='run_tree',
            name='behavior_tree_node',
            output='screen',
            parameters=[]
        ),
        
        # Command publisher node (opsiyonel, test için)
        Node(
            package='turtle_tasks',
            executable='command_publisher',
            name='command_publisher_node',
            output='screen',
            parameters=[]
        )
    ])

