#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Package names
    open_base_pkg = 'open_base'
    gazebo_pkg = 'gazebo_ros'
    
    # Launch RViz argument
    launch_rviz = LaunchConfiguration('launch_rviz')
    launch_rviz_arg = DeclareLaunchArgument(
        name='launch_rviz',
        default_value='False',
        description='True if to launch rviz, false otherwise'
    )
    
    # URDF file
    urdf_file = os.path.join(
        get_package_share_directory(open_base_pkg),
        'urdf',
        'description.urdf'
    )
    
    # RViz config
    rviz_config = os.path.join(
        get_package_share_directory(open_base_pkg),
        'config',
        'open_base.rviz'
    )
    
    # Controllers config
    controllers_config = os.path.join(
        get_package_share_directory(open_base_pkg),
        'config',
        'omnidirectional_controller.yaml'
    )
    
    # RViz node
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        condition=IfCondition(launch_rviz),
        arguments=['-d', rviz_config]
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
    
    # Controller manager
    controller_manager_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[controllers_config],
        output='screen'
    )
    
    # Joint state broadcaster spawner
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output='screen'
    )
    
    # Joint state broadcaster event handler
    joint_state_broadcaster_event_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner]
        )
    )
    
    # Omnidirectional controller spawner
    omni_base_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["omnidirectional_controller"],
        output='screen'
    )
    
    # Omnidirectional controller event handler
    omni_base_controller_event_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[omni_base_controller_spawner]
        )
    )
    
    # RViz event handler
    rviz_event_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=omni_base_controller_spawner,
            on_exit=[rviz_node]
        )
    )
    
    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(gazebo_pkg), 'launch'), '/gazebo.launch.py']),
    )
    
    return LaunchDescription([
        launch_rviz_arg,
        controller_manager_node,
        joint_state_broadcaster_event_handler,
        omni_base_controller_event_handler,
        robot_state_publisher_node,
        spawn_entity,
        gazebo,
        rviz_event_handler
    ])
