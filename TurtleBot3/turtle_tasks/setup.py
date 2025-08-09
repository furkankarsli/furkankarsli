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
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='furkan',
    maintainer_email='furknkrsli@gmail.com',
    description='TurtleBot tasks using py_trees and ROS 2',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'run_tree = turtle_tasks.run_tree:main',  # run_tree.py turtle_tasks/ dizininde
        ],
    },
)