import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'sentinel_brain'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bgenem',
    maintainer_email='bgenem@esalto.es',
    description='ROS2 Python package for a sentinel robot mission control system',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'status_node = sentinel_brain.status_node:main',
            'logger_server = sentinel_brain.logger_server:main',
            'incident_reporter = sentinel_brain.incident_reporter:main',
            'patrol_worker_node = sentinel_brain.patrol_worker_node:main',
            'patrol_action_server = sentinel_brain.patrol_action_server:main',
            'mission_control_client = sentinel_brain.mission_control_client:main',
        ],
    },
)