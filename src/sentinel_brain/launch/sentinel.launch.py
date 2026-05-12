from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Node 1: Heartbeat
        Node(
            package='sentinel_brain',
            executable='status_node',
            name='status_node'
        ),
        
        # Node 2: Logger
        Node(
            package='sentinel_brain',
            executable='logger_server',
            name='logger_server'
        )
    ])