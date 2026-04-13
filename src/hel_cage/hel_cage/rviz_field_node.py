import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, Vector3
from std_msgs.msg import ColorRGBA
import numpy as np

class RVizFullFieldPublisher(Node):
    def __init__(self):
        super().__init__('rviz_full_field_publisher')
        
        self.marker_pub = self.create_publisher(MarkerArray, 'magnetic_field_markers', 10)
        self.subscription = self.create_subscription(Vector3, 'telemetry', self.tel_cb, 10)
        
        self.get_logger().info('Initializing Full-Field Helmholtz Geometry...')
        self._setup_geometry()
        self._precompute_normalized_fields()
        
        self.get_logger().info('Ready. Displaying inside and outside field lines.')

    def _setup_geometry(self):
        """Expands the grid to see the return loops outside the 1m cage."""
        N = 12 # 12x12x12 = 1728 points (higher density)
        bound = 1.2 # Extends 0.7m past the coils on all sides
        
        x = np.linspace(-bound, bound, N)
        y = np.linspace(-bound, bound, N)
        z = np.linspace(-bound, bound, N)
        xg, yg, zg = np.meshgrid(x, y, z)
        
        self.grid_pos = np.vstack([xg.ravel(), yg.ravel(), zg.ravel()]).T

    def _dipole(self, pos, axis):
        """Standard dipole field equation."""
        mag = np.linalg.norm(pos, axis=1)
        mag = np.maximum(mag, 0.05) # Prevent division by zero at coil centers
        m = axis * 10.0 
        
        dot = np.sum(pos * m, axis=1)
        term1 = (3 * dot[:, None] * pos) / (mag[:, None]**5)
        term2 = m / (mag[:, None]**3)
        return term1 - term2

    def _precompute_normalized_fields(self):
        """Calculates the field shape and anchors the scale to the center point."""
        offset = 0.5 # Coils are at +/- 0.5m

        # 1. Generate raw shapes for all 1728 points
        raw_Fx = self._dipole(self.grid_pos - [offset, 0, 0], np.array([1, 0, 0])) + \
                 self._dipole(self.grid_pos - [-offset, 0, 0], np.array([1, 0, 0]))
                 
        raw_Fy = self._dipole(self.grid_pos - [0, offset, 0], np.array([0, 1, 0])) + \
                 self._dipole(self.grid_pos - [0, -offset, 0], np.array([0, 1, 0]))
                 
        raw_Fz = self._dipole(self.grid_pos - [0, 0, offset], np.array([0, 0, 1])) + \
                 self._dipole(self.grid_pos - [0, 0, -offset], np.array([0, 0, 1]))

        # 2. Calculate the exact theoretical value at the Center (0,0,0)
        center_pos = np.array([[0.0, 0.0, 0.0]])
        center_Fx = self._dipole(center_pos - [offset, 0, 0], np.array([1, 0, 0])) + \
                    self._dipole(center_pos - [-offset, 0, 0], np.array([1, 0, 0]))
        center_Fy = self._dipole(center_pos - [0, offset, 0], np.array([0, 1, 0])) + \
                    self._dipole(center_pos - [0, -offset, 0], np.array([0, 1, 0]))
        center_Fz = self._dipole(center_pos - [0, 0, offset], np.array([0, 0, 1])) + \
                    self._dipole(center_pos - [0, 0, -offset], np.array([0, 0, 1]))

        # 3. Normalize the matrices so the center multiplier is exactly 1.0
        self.Fx = raw_Fx / center_Fx[0, 0]
        self.Fy = raw_Fy / center_Fy[0, 1]
        self.Fz = raw_Fz / center_Fz[0, 2]

    def tel_cb(self, msg):
        # The live telemetry is now directly scaling a normalized 3D map
        B = (self.Fx * msg.x) + (self.Fy * msg.y) + (self.Fz * msg.z)
        
        mag = np.linalg.norm(B, axis=1)
        norm_color = np.clip(mag / 100.0, 0.0, 1.0) 
        
        # We increase the visual vector scaling slightly so weak return lines are visible
        vis_vectors = B * 0.08 
        cap_limit = 0.20
        
        actual_mag = np.linalg.norm(vis_vectors, axis=1)
        clipped_mag = np.minimum(actual_mag, cap_limit)
        safe_mag = np.maximum(actual_mag, 1e-6)
        final_vectors = (vis_vectors / safe_mag[:, None]) * clipped_mag[:, None]

        marker_array = MarkerArray()
        timestamp = self.get_clock().now().to_msg()
        
        for i in range(len(self.grid_pos)):
            marker = Marker()
            marker.header.frame_id = "cage_center"
            marker.header.stamp = timestamp
            marker.ns = "mag_field_full"
            marker.id = i
            marker.type = Marker.ARROW
            marker.action = Marker.ADD 
            
            start = Point(x=float(self.grid_pos[i,0]), y=float(self.grid_pos[i,1]), z=float(self.grid_pos[i,2]))
            end = Point(
                x=float(self.grid_pos[i,0] + final_vectors[i,0]),
                y=float(self.grid_pos[i,1] + final_vectors[i,1]),
                z=float(self.grid_pos[i,2] + final_vectors[i,2])
            )
            marker.points = [start, end]
            
            # Make the arrows slightly thinner to accommodate the higher density grid
            marker.scale.x = 0.008 
            marker.scale.y = 0.015 
            marker.scale.z = 0.015 
            
            marker.color = ColorRGBA(
                r=float(norm_color[i]),
                g=float(0.2 + 0.8 * (1.0 - norm_color[i])),
                b=1.0,
                a=0.8
            )
            marker_array.markers.append(marker)
            
        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(RVizFullFieldPublisher())
    rclpy.shutdown()

if __name__ == '__main__':
    main()