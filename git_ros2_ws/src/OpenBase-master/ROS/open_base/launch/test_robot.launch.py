#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directories
    open_base_pkg = get_package_share_directory('open_base')
    
    # Launch arguments
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='false')
    
    # Robot state publisher for our robot
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'robot_description': open(os.path.join(open_base_pkg, 'urdf', 'description.urdf'), 'r').read()
        }]
    )
    
    # Joint state publisher
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )
    
    # RViz with basic configuration
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=[],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        robot_state_publisher_node,
        joint_state_publisher_node,
        rviz_node
    ])

