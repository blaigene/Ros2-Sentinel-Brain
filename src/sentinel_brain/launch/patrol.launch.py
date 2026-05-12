from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from os.path import join

def generate_launch_description():
    config_file = join(
        get_package_share_directory('sentinel_brain'),
        'config', 
        'patrol_params.yaml'
    )
    
    return LaunchDescription([
        Node(
            package='sentinel_brain',
            executable='status_node',
            name='status_node',
            output='screen'
        ),
        Node(
            package='sentinel_brain',
            executable='patrol_worker_node',
            name='patrol_worker',
            output='screen',
            parameters=[config_file]
        )
    ])