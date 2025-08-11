from setuptools import find_packages, setup

package_name = 'smach_101'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='furkan',
    maintainer_email='furknkrsli@gmail.com',
    description='ROS2 SMACH State Machine Implementation',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'smach_example = smach_101.simple_smach:main',
        ],
    }
)