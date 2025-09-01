#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directories
    open_base_pkg = get_package_share_directory('open_base')
    
    # Use simple URDF
    urdf_file = os.path.join(open_base_pkg, 'urdf', 'simple_test.urdf')
    
    # Launch Gazebo server with plugins
    gazebo_server = ExecuteProcess(
        cmd=['gzserver', '--verbose', '/opt/ros/humble/share/gazebo_ros/worlds/empty.world', 
             '-s', 'libgazebo_ros_init.so', 
             '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )
    
    # Launch Gazebo client
    gazebo_client = ExecuteProcess(
        cmd=['gzclient', '--verbose'],
        output='screen'
    )
    
    # Robot state publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': open(urdf_file, 'r').read()
        }]
    )
    
    # Spawn robot
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'open_base_simple',
            '-file', urdf_file,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo_server,
        gazebo_client,
        robot_state_publisher_node,
        spawn_entity_node
    ])
