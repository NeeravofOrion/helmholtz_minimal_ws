import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'hel_cage'

   
    return LaunchDescription([

        # ==========================================
        # 1. CORE SYSTEM NODES (Your original setup)
        # ==========================================
        Node(
            package='hel_cage',
            executable='bridge_node',
            name='bridge_node',
            output='screen'
        ),
       
        Node(
            package='hel_cage',
            executable='control_node',
            name='control_node',
            output='screen'
        ),
        Node(
            package='hel_cage',
            executable='calibration_node',
            name='calibration_node',
            output='screen'
        ),
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