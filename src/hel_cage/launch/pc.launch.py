import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'hel_cage'

    # ==========================================
    # FILE PATHS FOR VISUALIZATION
    # ==========================================
    # Assumes you have a 'urdf' folder inside your package
    urdf_file = os.path.join(
        get_package_share_directory(package_name),
        'urdf',
        'helmholtz_cage.urdf'  # <--- CHANGE THIS to your actual URDF file name
    )
    
    # Assumes you have an 'rviz' folder inside your package
    rviz_config_file = os.path.join(
        get_package_share_directory(package_name),
        'rviz',
        'cage_view.rviz'  # <--- CHANGE THIS to your saved RViz config file name
    )

    # Read the URDF file into a string
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([

        # ==========================================
        # 1. CORE SYSTEM NODES (Your original setup)
        # ==========================================
        
        Node(
            package='hel_cage',
            executable='gui_node',
            name='gui_node',
            output='screen'
        ),
        
        # ==========================================
        # 2. DIGITAL TWIN & VISUALIZATION (New)
        # ==========================================
        # Loads the physical 3D model of your cage
        
        Node(
            package='hel_cage',
            executable='rviz_field_node',
            name='rviz_field_node',
            output='screen'
        ),
        # Calculates and publishes the live magnetic field arrows
        
        
        # Opens RViz2 automatically with your saved layout
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file]
        ),
    ])
