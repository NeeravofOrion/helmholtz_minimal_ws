import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, Vector3
from std_msgs.msg import ColorRGBA
import numpy as np
import os

class RVizLiveFieldPublisher(Node):
    def __init__(self):
        super().__init__('rviz_live_field_publisher')
        
        # Publisher for RViz
        self.marker_pub = self.create_publisher(MarkerArray, 'magnetic_field_markers', 10)
        
        # Subscriber for live telemetry from the Pi/Cage
        self.subscription = self.create_subscription(
            Vector3, 
            'telemetry', 
            self.telemetry_callback, 
            10)
        
        # Setup Grid and Math
        self.get_logger().info('Initializing 1m x 1m Helmholtz geometry...')
        self._setup_geometry()
        self._precompute_fields()
        
        self.get_logger().info('Field matrices ready. Listening to /telemetry...')

    def _setup_geometry(self):
        """Defines the 3D grid points inside the 1m cage."""
        # Since the cage is 1m, the coils are at +/- 0.5m.
        # We set the grid boundary to 0.4m to keep arrows inside the frame.
        N = 10 
        bound = 0.4 
        
        x = np.linspace(-bound, bound, N)
        y = np.linspace(-bound, bound, N)
        z = np.linspace(-bound, bound, N)
        xg, yg, zg = np.meshgrid(x, y, z)
        
        # Store positions as a (1000, 3) array
        self.grid_pos = np.vstack([xg.ravel(), yg.ravel(), zg.ravel()]).T

    def _precompute_fields(self):
        """Calculates the unit influence for each coil pair."""
        # Physical separation is 50cm, so offset from center is 0.25m
        offset = 0.5 / 2.0 

        def dipole_field(pos, axis):
            """Calculates field lines for visualization purposes."""
            r = pos
            mag = np.linalg.norm(r, axis=1)
            mag = np.maximum(mag, 0.05) # Prevent division by zero
            m = axis * 10.0 # Strength factor for visual scaling
            
            dot = np.sum(r * m, axis=1)
            term1 = (3 * dot[:, None] * r) / (mag[:, None]**5)
            term2 = m / (mag[:, None]**3)
            return term1 - term2

        # Precompute the 'shape' of the field for each axis
        self.Fx = dipole_field(self.grid_pos - [offset, 0, 0], np.array([1, 0, 0])) + \
                  dipole_field(self.grid_pos - [-offset, 0, 0], np.array([1, 0, 0]))
                  
        self.Fy = dipole_field(self.grid_pos - [0, offset, 0], np.array([0, 1, 0])) + \
                  dipole_field(self.grid_pos - [0, -offset, 0], np.array([0, 1, 0]))
                  
        self.Fz = dipole_field(self.grid_pos - [0, 0, offset], np.array([0, 0, 1])) + \
                  dipole_field(self.grid_pos - [0, 0, -offset], np.array([0, 0, 1]))

    def telemetry_callback(self, msg):
        """Calculates and publishes the MarkerArray based on live Vector3 data."""
        # 1. Scale precomputed matrices by live readings
        B = (self.Fx * msg.x) + (self.Fy * msg.y) + (self.Fz * msg.z)
        
        # 2. Magnitude and Color Scaling
        mag = np.linalg.norm(B, axis=1)
        # Normalize color based on intensity (0 to 100uT range)
        norm_color = np.clip(mag / 100.0, 0.0, 1.0) 
        
        # 3. Vector Visual Sizing
        # We cap the arrow length so it doesn't clutter the screen
        vis_vectors = B * 0.05 
        cap_limit = 0.15
        actual_mag = np.linalg.norm(vis_vectors, axis=1)
        clipped_mag = np.minimum(actual_mag, cap_limit)
        
        # Avoid zero-length arrows to prevent RViz errors
        safe_mag = np.maximum(actual_mag, 1e-6)
        final_vectors = (vis_vectors / safe_mag[:, None]) * clipped_mag[:, None]

        # 4. Create the Marker Message
        marker_array = MarkerArray()
        timestamp = self.get_clock().now().to_msg()
        
        for i in range(len(self.grid_pos)):
            marker = Marker()
            marker.header.frame_id = "cage_center"
            marker.header.stamp = timestamp
            marker.ns = "mag_field"
            marker.id = i
            marker.type = Marker.ARROW
            marker.action = Marker.ADD # Or Marker.MODIFY
            
            # Set Arrow Start (Grid Position) and End (Field Direction)
            start = Point(x=float(self.grid_pos[i,0]), y=float(self.grid_pos[i,1]), z=float(self.grid_pos[i,2]))
            end = Point(
                x=float(self.grid_pos[i,0] + final_vectors[i,0]),
                y=float(self.grid_pos[i,1] + final_vectors[i,1]),
                z=float(self.grid_pos[i,2] + final_vectors[i,2])
            )
            marker.points = [start, end]
            
            # Arrow head/shaft thickness
            marker.scale.x = 0.01 # Shaft diameter
            marker.scale.y = 0.02 # Head diameter
            marker.scale.z = 0.02 # Head length
            
            # Dynamic Color (Blue is weak, White/Red is strong)
            marker.color = ColorRGBA(
                r=float(norm_color[i]),
                g=float(0.3 + 0.7 * (1.0 - norm_color[i])),
                b=1.0,
                a=0.7 # Slight transparency to see through the field
            )
            
            marker_array.markers.append(marker)
            
        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    node = RVizLiveFieldPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()