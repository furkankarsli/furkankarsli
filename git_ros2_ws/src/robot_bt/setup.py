from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'robot_bt'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'behavior_trees'), glob('behavior_trees/*.xml')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools', 'py_trees', 'py_trees_ros', 'rclpy', 'geometry_msgs', 'sensor_msgs', 'std_msgs', 'nav2_msgs', 'std_srvs'],
    zip_safe=True,
    maintainer='furkan',
    maintainer_email='furknkrsli@gmail.com',
    description='Robot Behavior Tree package.',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'clean_area_service = robot_bt.clean_action_server:main',
            'move_action_server = robot_bt.move_action_server:main',
            'battery_state_publisher = robot_bt.battery_state_publisher:main',
            'distance_sensor_publisher = robot_bt.distance_sensor_publisher:main',
            'cmd_vel_publisher = robot_bt.cmd_vel_publisher:main',
            'bt_executor = robot_bt.bt_executor:main',
            'emergency_publisher = robot_bt.emergency_publisher:main',
            'user_command_interface = robot_bt.user_command_interface:main',
            'log_manager = robot_bt.log_manager:main',
        ],
    },
)