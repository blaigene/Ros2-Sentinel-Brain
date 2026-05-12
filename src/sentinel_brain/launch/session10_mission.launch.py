from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from os.path import join


def generate_launch_description():
    mission_file = join(
        get_package_share_directory('sentinel_brain'),
        'config',
        'mission_file.yaml'
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
            executable='patrol_action_server',
            name='patrol_action_server',
            output='screen'
        ),
        Node(
            package='sentinel_brain',
            executable='mission_control_client',
            name='mission_control_client',
            output='screen',
            parameters=[{'mission_file': mission_file}]
        ),
    ])
