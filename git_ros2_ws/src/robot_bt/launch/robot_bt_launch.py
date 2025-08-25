from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_bt',
            executable='emergency_publisher',
            name='emergency_publisher',
            output='screen'
        ),
        Node(
            package='robot_bt',
            executable='battery_state_publisher',
            name='battery_state_publisher',
            output='screen'
        ),
        Node(
            package='robot_bt',
            executable='distance_sensor_publisher',
            name='distance_sensor_publisher',
            output='screen'
        ),
        Node(
            package='robot_bt',
            executable='cmd_vel_publisher',
            name='cmd_vel_publisher',
            output='screen'
        ),
        Node(
            package='robot_bt',
            executable='clean_area_service',
            name='clean_area_service',
            output='screen'
        ),
        Node(
            package='robot_bt',
            executable='move_action_server',
            name='move_action_server',
            output='screen'
        ),
        Node(
            package='robot_bt',
            executable='bt_executor',
            name='bt_executor',
            output='screen',
            emulate_tty=True # For coloured console output
        ),
        Node(
            package='robot_bt',
            executable='user_command_interface',
            name='user_command_interface',
            output='screen',
            emulate_tty=True
        ),
    ])