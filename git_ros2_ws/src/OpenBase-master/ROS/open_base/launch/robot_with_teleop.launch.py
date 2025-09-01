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
    
    # Launch arguments
    use_keyboard_arg = DeclareLaunchArgument('use_keyboard', default_value='true')
    use_joystick_arg = DeclareLaunchArgument('use_joystick', default_value='false')
    
    # Use REAL robot URDF
    urdf_file = os.path.join(open_base_pkg, 'urdf', 'description.urdf')
    
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
        name='controller_manager',
        output='screen',
        parameters=[
            os.path.join(open_base_pkg, 'config', 'controllers.yaml')
        ]
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
    
    # Spawn controllers
    spawn_controllers = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', 'left_wheel_controller', 'right_wheel_controller', 'back_wheel_controller'],
        output='screen'
    )
    
    # Keyboard teleop
    keyboard_teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='keyboard_teleop',
        output='screen',
        remappings=[('cmd_vel', '/open_base/cmd_vel')]
    )
    
    # Joystick teleop
    joystick_teleop = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='joystick_teleop',
        output='screen',
        remappings=[('cmd_vel', '/open_base/cmd_vel')]
    )
    
    return LaunchDescription([
        use_keyboard_arg,
        use_joystick_arg,
        gazebo_server,
        gazebo_client,
        robot_state_publisher_node,
        controller_manager_node,
        spawn_entity_node,
        spawn_controllers,
        keyboard_teleop,
        joystick_teleop
    ])
