from setuptools import setup

package_name = 'turtle_tasks'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/launch.py']),
        ('share/' + package_name + '/params', ['params/nav2_params.yaml']),
        ('share/' + package_name + '/poses', ['turtle_tasks/poses.yaml']),
    ],
    install_requires=['setuptools', 'PyYAML'],
    zip_safe=True,
    maintainer='furkan',
    maintainer_email='furknkrsli@gmail.com',
    description='TurtleBot tasks using py_trees and ROS 2',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'run_tree = turtle_tasks.run_tree:main',
            'command_publisher = turtle_tasks.command_publisher:main',
            'test_nav2 = turtle_tasks.test_nav2:main',
            'debug_robot = turtle_tasks.debug_robot:main',
            'quick_test = turtle_tasks.quick_test:main',
        ],
    },
)