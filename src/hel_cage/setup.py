import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'hel_cage'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        (
            'share/' + package_name,
            ['package.xml'],
        ),
        # Grabs ALL launch files (both system.launch.py and cage_bringup.launch.py)
        (
            os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.[pxy][yma]*')),
        ),
        # Grabs your 3D URDF model files
        (
            os.path.join('share', package_name, 'urdf'),
            glob('urdf/*'),
        ),
        # Grabs your saved RViz visual layouts
        (
            os.path.join('share', package_name, 'rviz'),
            glob('rviz/*'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='neerav',
    maintainer_email='22311a1901@ecm.sreenidhi.edu.in',
    description='Helmholtz cage ROS2 interface with GUI and serial bridge',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'gui_node = hel_cage.gui_node:main',
            'bridge_node = hel_cage.bridge_node:main',
            'cmd_publisher = hel_cage.cmd_publisher:main',
            'fft_node = hel_cage.fft_node:main',
            'control_node = hel_cage.control_node:main',
            'calibration_node = hel_cage.calibration_node:main',
            'data_logger_node = hel_cage.data_logger_node:main',
            'variable_field_node = hel_cage.variable_field_node:main',
            'rviz_field_node = hel_cage.rviz_field_node:main',
        ],
    },
)