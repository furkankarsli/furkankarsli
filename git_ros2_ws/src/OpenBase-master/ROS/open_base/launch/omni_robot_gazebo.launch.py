#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directories
    open_base_pkg = get_package_share_directory('open_base')
    
    # Use REAL robot URDF (omnidirectional)
    urdf_file = os.path.join(open_base_pkg, 'urdf', 'description.urdf')
    
    # Controller configuration
    controllers_config = os.path.join(open_base_pkg, 'config', 'omni_controllers.yaml')
    
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
    
    # Controller manager
    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[controllers_config],
        output='screen'
    )
    
    # Spawn controllers
    spawn_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen'
    )
    
    spawn_omni_velocity_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['omni_velocity_controller'],
        output='screen'
    )
    
    # Spawn robot
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'open_base',
            '-file', urdf_file,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1'
        ],
        output='screen'
    )
    
    # Teleop nodes (optional)
    teleop_keyboard = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='keyboard_teleop',
        output='screen',
        remappings=[
            ('cmd_vel', '/open_base/cmd_vel')
        ]
    )
    
    teleop_joy = Node(
        package='teleop_twist_joy',
        executable='teleop_twist_joy_node',
        name='joy_teleop',
        output='screen',
        remappings=[
            ('cmd_vel', '/open_base/cmd_vel')
        ]
    )
    
    return LaunchDescription([
        gazebo_server,
        gazebo_client,
        robot_state_publisher_node,
        controller_manager_node,
        spawn_joint_state_broadcaster,
        spawn_omni_velocity_controller,
        spawn_entity_node,
        teleop_keyboard,
        teleop_joy
    ])
