#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package directories
    open_base_pkg = get_package_share_directory('open_base')
    gazebo_pkg = get_package_share_directory('gazebo_ros')
    turtlebot3_gazebo_pkg = get_package_share_directory('turtlebot3_gazebo')
    
    # Launch arguments
    gui_arg = DeclareLaunchArgument('gui', default_value='true')
    paused_arg = DeclareLaunchArgument('paused', default_value='false')
    use_sim_time_arg = DeclareLaunchArgument('use_sim_time', default_value='true')
    x_pose_arg = DeclareLaunchArgument('x_pose', default_value='0.0')
    y_pose_arg = DeclareLaunchArgument('y_pose', default_value='0.0')
    
    # Use empty world for faster loading
    world = os.path.join(
        turtlebot3_gazebo_pkg,
        'worlds',
        'empty_world.world'
    )
    
    # Launch Gazebo server with plugins
    gazebo_server = ExecuteProcess(
        cmd=['gzserver', '--verbose', world, '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so'],
        output='screen'
    )
    
    # Launch Gazebo client
    gazebo_client = ExecuteProcess(
        cmd=['gzclient', '--verbose'],
        output='screen'
    )
    
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
    
    # Spawn our robot in the world
    spawn_entity_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'open_base',
            '-file', os.path.join(open_base_pkg, 'urdf', 'description.urdf'),
            '-x', LaunchConfiguration('x_pose'),
            '-y', LaunchConfiguration('y_pose'),
            '-z', '0.0'
        ],
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
        gui_arg,
        paused_arg,
        use_sim_time_arg,
        x_pose_arg,
        y_pose_arg,
        gazebo_server,
        gazebo_client,
        robot_state_publisher_node,
        joint_state_publisher_node,
        spawn_entity_node,
        rviz_node
    ])


