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
        (
            'share/' + package_name + '/launch',
            ['launch/system.launch.py'],
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
        ],
    },
)