from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('sentinel_description')
    slam_params_file = os.path.join(pkg_share, 'config', 'mapper_params_online_async.yaml')
    
    gazebo_launch = PathJoinSubstitution(
        [FindPackageShare('sentinel_description'), 'launch', 'sentinel_gazebo.launch.py']
    )
    
    slam_toolbox_launch = PathJoinSubstitution(
        [FindPackageShare('slam_toolbox'), 'launch', 'online_async_launch.py']
    )
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch)
    )
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_toolbox_launch),
        launch_arguments={'use_sim_time': 'true', 'slam_params_file': slam_params_file}.items()
    )
    return LaunchDescription([
        gazebo,
        slam_toolbox
    ])