#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    # Package names
    open_base_pkg = 'open_base'
    gazebo_pkg = 'gazebo_ros'
    
    # URDF file
    urdf_file = os.path.join(
        get_package_share_directory(open_base_pkg),
        'urdf',
        'description.urdf'
    )
    
    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': open(urdf_file, 'r').read()}],
    )
    
    # Spawn robot
    spawn_entity = Node(
        package='gazebo_ros', 
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'open_base'],
        output='screen'
    )
    
    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(gazebo_pkg), 'launch'), '/gazebo.launch.py']),
    )
    
    return LaunchDescription([
        gazebo,
        robot_state_publisher_node,
        spawn_entity
    ])

