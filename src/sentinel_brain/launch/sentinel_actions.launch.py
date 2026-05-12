from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='sentinel_brain',
            executable='status_node',
            arguments=['--ros-args', '--log-level', 'error']
        ),
        Node(
            package='sentinel_brain',
            executable='patrol_action_server',
        ),
        Node(
            package='sentinel_brain',
            executable='mission_control_client',
        ),
    ])