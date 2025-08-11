from setuptools import find_packages, setup

package_name = 'turtlebot_autonomy'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/mission.launch.py']),
        ('share/' + package_name + '/param', ['param/mission_params.yaml']), # BU SATIRIN EKLENDİĞİNDEN EMİN OL
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='furkan',
    maintainer_email='furkan@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_state_machine = turtlebot_autonomy.mission_state_machine:main',
        ],
    },
)