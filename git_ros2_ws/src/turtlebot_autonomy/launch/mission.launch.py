# mission.launch.py
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('turtlebot_autonomy')
    # mission_params.yaml artık doğrudan Smach düğümüne yüklenmeyecek.
    # params_file = os.path.join(pkg_dir, 'param', 'mission_params.yaml') 

    return LaunchDescription([
        Node(
            package='turtlebot_autonomy',
            executable='mission_state_machine',
            name='mission_state_machine_node',
            output='screen',
            # parameters=[params_file] # Bu satır artık kullanılmayacak
        )
    ])