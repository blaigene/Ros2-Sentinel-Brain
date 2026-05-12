from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
from launch.actions import TimerAction

import os


def generate_launch_description():

    pkg_share = get_package_share_directory('sentinel_description')

    map_file = os.path.join(
        pkg_share,
        'maps',
        'warehouse_map.yaml'
    )

    nav2_params_file = os.path.join(
        pkg_share,
        'config',
        'nav2_params.yaml'
    )

    gazebo_launch = PathJoinSubstitution([
        FindPackageShare('sentinel_description'),
        'launch',
        'sentinel_gazebo.launch.py'
    ])

    nav2_launch = PathJoinSubstitution([
        FindPackageShare('nav2_bringup'),
        'launch',
        'bringup_launch.py'
    ])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch)
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch),
        launch_arguments={
            'use_sim_time': 'True',
            'map': map_file,
            'params_file': nav2_params_file,
            'autostart': 'True',
            'slam': 'False',
            'use_collision_monitor': 'False',
            'use_docking': 'False'
        }.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        nav2,
        rviz
    ])