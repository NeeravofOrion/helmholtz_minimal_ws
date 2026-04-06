from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([

        Node(
            package='hel_cage',
            executable='bridge_node',
            name='bridge_node',
            output='screen'
        ),

        Node(
            package='hel_cage',
            executable='gui_node',
            name='gui_node',
            output='screen'
        ),

    ])