#!/bin/bash

echo "🚀 Starting Helmholtz Cage..."
ros2 launch hel_cage system.launch.py

# The script will pause here until you press Ctrl+C to kill ROS 2.
# Once ROS 2 is dead, it moves to the next line automatically.

echo "🛑 Test finished. Transferring data to PC..."
~/helmholtz_minimal_ws/send_log.sh
