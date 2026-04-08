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
        
        Node(
            package='hel_cage',
            executable='control_node',
            name='control_node',
            output='screen'
        ),

        # ===== NEW: CALIBRATION NODE =====
        Node(
            package='hel_cage',
            executable='calibration_node',
            name='calibration_node',
            output='screen'
        ),

        # ===== NEW: DATA LOGGER =====
        Node(
            package='hel_cage',
            executable='data_logger_node',
            name='data_logger',
            output='screen'
        ),
        Node(
            package='hel_cage',
            executable='variable_field_node',
            name='variable_field_node',
         output='screen'
        ),
    ])