import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'pytree_101'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # EKSİK OLAN VE HATAYA NEDEN OLAN SATIR BURAYA EKLENDİ
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yeml]'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='furkan',
    maintainer_email='furknkrsli@gmail.com',
    description='A basic PyTree example with ROS 2 integration for battery monitoring',
    license='MIT-0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pytree_example = pytree_101.pytree_node3:main',
            'battery_bt_node = pytree_101.battery_bt_node:main',
            'pytree_node = pytree_101.main:main',
        ],
    },
)
from setuptools import setup

package_name = 'pytree_101'

