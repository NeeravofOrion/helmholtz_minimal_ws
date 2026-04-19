#!/usr/bin/env python3
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
        
        # VISUAL SCALING CONSTANT: How long the center arrows get per µT
        self.center_scale = 0.005 # 100 µT = 0.5 meters long in RViz

        self.get_logger().info('Initializing Full-Field Helmholtz Geometry...')
        self._setup_geometry()
        self._precompute_normalized_fields()
        
        self.get_logger().info('Ready. Displaying inside and outside field lines plus external vectors.')

    def _setup_geometry(self):
        """Expands the grid to see the return loops outside the 1m cage."""
        N = 12 # 12x12x12 = 1728 points
        bound = 1.2 
        
        x = np.linspace(-bound, bound, N)
        y = np.linspace(-bound, bound, N)
        z = np.linspace(-bound, bound, N)
        xg, yg, zg = np.meshgrid(x, y, z)
        
        self.grid_pos = np.vstack([xg.ravel(), yg.ravel(), zg.ravel()]).T

    def _dipole(self, pos, axis):
        """Standard dipole field equation."""
        mag = np.linalg.norm(pos, axis=1)
        mag = np.maximum(mag, 0.05) 
        m = axis * 10.0 
        
        dot = np.sum(pos * m, axis=1)
        term1 = (3 * dot[:, None] * pos) / (mag[:, None]**5)
        term2 = m / (mag[:, None]**3)
        return term1 - term2

    def _precompute_normalized_fields(self):
        """Calculates the field shape and anchors the scale to the center point."""
        offset = 0.5 

        raw_Fx = self._dipole(self.grid_pos - [offset, 0, 0], np.array([1, 0, 0])) + \
                 self._dipole(self.grid_pos - [-offset, 0, 0], np.array([1, 0, 0]))
                 
        raw_Fy = self._dipole(self.grid_pos - [0, offset, 0], np.array([0, 1, 0])) + \
                 self._dipole(self.grid_pos - [0, -offset, 0], np.array([0, 1, 0]))
                 
        raw_Fz = self._dipole(self.grid_pos - [0, 0, offset], np.array([0, 0, 1])) + \
                 self._dipole(self.grid_pos - [0, 0, -offset], np.array([0, 0, 1]))

        center_pos = np.array([[0.0, 0.0, 0.0]])
        center_Fx = self._dipole(center_pos - [offset, 0, 0], np.array([1, 0, 0])) + \
                    self._dipole(center_pos - [-offset, 0, 0], np.array([1, 0, 0]))
        center_Fy = self._dipole(center_pos - [0, offset, 0], np.array([0, 1, 0])) + \
                    self._dipole(center_pos - [0, -offset, 0], np.array([0, 1, 0]))
        center_Fz = self._dipole(center_pos - [0, 0, offset], np.array([0, 0, 1])) + \
                    self._dipole(center_pos - [0, 0, -offset], np.array([0, 0, 1]))

        self.Fx = raw_Fx / center_Fx[0, 0]
        self.Fy = raw_Fy / center_Fy[0, 1]
        self.Fz = raw_Fz / center_Fz[0, 2]

    def _create_center_arrow(self, arrow_id, vec_x, vec_y, vec_z, r, g, b, thickness=0.015):
        """Generates a structural marker anchored at a static external offset."""
        marker = Marker()
        marker.header.frame_id = "cage_center"
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = "external_vectors"
        marker.id = arrow_id
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        
        # Define the external structural origin
        origin_x, origin_y, origin_z = 1.5, 1.5, 1.5

        # Structural safeguard against 0-length RViz warnings
        if abs(vec_x) < 1e-4 and abs(vec_y) < 1e-4 and abs(vec_z) < 1e-4:
            vec_x = 1e-4

        start = Point(x=origin_x, y=origin_y, z=origin_z)
        end = Point(x=origin_x + float(vec_x), y=origin_y + float(vec_y), z=origin_z + float(vec_z))
        marker.points = [start, end]
        
        marker.scale.x = thickness * 2  # Shaft diameter
        marker.scale.y = thickness * 4  # Head diameter
        marker.scale.z = thickness * 4  # Head length
        
        marker.color = ColorRGBA(r=float(r), g=float(g), b=float(b), a=1.0)
        return marker

    def tel_cb(self, msg):
        # 1. PROCESS GRID FIELD
        B = (self.Fx * msg.x) + (self.Fy * msg.y) + (self.Fz * msg.z)
        mag = np.linalg.norm(B, axis=1)
        norm_color = np.clip(mag / 100.0, 0.0, 1.0) 
        
        vis_vectors = B * 0.08 
        cap_limit = 0.20
        
        actual_mag = np.linalg.norm(vis_vectors, axis=1)
        clipped_mag = np.minimum(actual_mag, cap_limit)
        safe_mag = np.maximum(actual_mag, 1e-6)
        final_vectors = (vis_vectors / safe_mag[:, None]) * clipped_mag[:, None]

        marker_array = MarkerArray()
        
        # Build Grid Background
        for i in range(len(self.grid_pos)):
            marker = Marker()
            marker.header.frame_id = "cage_center"
            marker.header.stamp = self.get_clock().now().to_msg()
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
            
        # 2. PROCESS EXTERNAL VECTORS
        # X Axis Component (Red)
        marker_array.markers.append(self._create_center_arrow(
            arrow_id=10000, 
            vec_x=msg.x * self.center_scale, vec_y=0.0, vec_z=0.0, 
            r=1.0, g=0.0, b=0.0
        ))
        
        # Y Axis Component (Green)
        marker_array.markers.append(self._create_center_arrow(
            arrow_id=10001, 
            vec_x=0.0, vec_y=msg.y * self.center_scale, vec_z=0.0, 
            r=0.0, g=1.0, b=0.0
        ))
        
        # Z Axis Component (Blue)
        marker_array.markers.append(self._create_center_arrow(
            arrow_id=10002, 
            vec_x=0.0, vec_y=0.0, vec_z=msg.z * self.center_scale, 
            r=0.0, g=0.5, b=1.0
        ))

        # Resultant Vector (Yellow, Thicker)
        marker_array.markers.append(self._create_center_arrow(
            arrow_id=10003, 
            vec_x=msg.x * self.center_scale, 
            vec_y=msg.y * self.center_scale, 
            vec_z=msg.z * self.center_scale, 
            r=1.0, g=1.0, b=0.0,
            thickness=0.025
        ))
            
        self.marker_pub.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(RVizFullFieldPublisher())
    rclpy.shutdown()

if __name__ == '__main__':
    main()