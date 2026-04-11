import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point, Vector3
from std_msgs.msg import ColorRGBA
import numpy as np

class RVizLiveFieldPublisher(Node):
    def __init__(self):
        super().__init__('rviz_live_field_publisher')
        
        # Publisher for RViz
        self.publisher_ = self.create_publisher(MarkerArray, 'magnetic_field_markers', 10)
        
        # SUBSCRIBER for your live data
        # Ensure 'telemetry' matches your actual topic name in your bridge/control nodes
        self.subscription = self.create_subscription(
            Vector3, 
            'telemetry', 
            self.telemetry_callback, 
            10)
        
        # Setup Grid and Math
        self.get_logger().info('Pre-calculating field matrices...')
        self._setup_geometry()
        self._precompute_fields()
        
        self.get_logger().info('Listening to /telemetry... Open RViz2 to view live field!')

    def _setup_geometry(self):
        cage_size = 6.0
        N = 10 
        bound = cage_size * 0.75
        
        x = np.linspace(-bound, bound, N)
        y = np.linspace(-bound, bound, N)
        z = np.linspace(-bound, bound, N)
        xg, yg, zg = np.meshgrid(x, y, z)
        self.grid_pos = np.vstack([xg.ravel(), yg.ravel(), zg.ravel()]).T

    def _precompute_fields(self):
        offset = 6.0 * 0.5445 / 2.0

        def field(pos, axis):
            r = pos
            mag = np.linalg.norm(r, axis=1)
            mag = np.maximum(mag, 0.1)
            m = axis * 100.0
            dot = np.sum(r * m, axis=1)
            term1 = (3 * dot[:, None] * r) / (mag[:, None]**5)
            term2 = m / (mag[:, None]**3)
            return term1 - term2

        self.Fx = field(self.grid_pos - [offset, 0, 0], np.array([1, 0, 0])) + \
                  field(self.grid_pos - [-offset, 0, 0], np.array([1, 0, 0]))
        self.Fy = field(self.grid_pos - [0, offset, 0], np.array([0, 1, 0])) + \
                  field(self.grid_pos - [0, -offset, 0], np.array([0, 1, 0]))
        self.Fz = field(self.grid_pos - [0, 0, offset], np.array([0, 0, 1])) + \
                  field(self.grid_pos - [0, 0, -offset], np.array([0, 0, 1]))

    def telemetry_callback(self, msg):
        # 1. EXTRACT LIVE DATA
        # (Assuming your Vector3 msg contains the values in microtesla)
        bx = msg.x
        by = msg.y
        bz = msg.z

        # 2. CALCULATE LIVE VECTOR FIELD
        B = self.Fx * bx + self.Fy * by + self.Fz * bz
        
        # 3. CALCULATE VISUALS
        mag = np.linalg.norm(B, axis=1)
        # Assuming 100uT is still the max expected value for color scaling
        norm = np.clip(mag / 100.0, 0.0, 1.0) 
        
        vis_vectors = B * 0.1
        cap_magnitude = 0.8
        vis_vectors_mag = np.linalg.norm(vis_vectors, axis=1)
        vis_vectors_mag_clipped = np.minimum(vis_vectors_mag, cap_magnitude)
        
        safe_mag = np.maximum(vis_vectors_mag, 1e-6)
        final_vis_vectors = (vis_vectors / safe_mag[:, None]) * vis_vectors_mag_clipped[:, None]

        # 4. BUILD MARKER ARRAY
        marker_array = MarkerArray()
        current_time = self.get_clock().now().to_msg()
        
        for i in range(len(self.grid_pos)):
            marker = Marker()
            marker.header.frame_id = "cage_center"
            marker.header.stamp = current_time
            marker.ns = "magnetic_field"
            marker.id = i
            marker.type = Marker.ARROW
            marker.action = Marker.MODIFY
            
            start_pt = Point(x=self.grid_pos[i,0], y=self.grid_pos[i,1], z=self.grid_pos[i,2])
            end_pt = Point(
                x=self.grid_pos[i,0] + final_vis_vectors[i,0],
                y=self.grid_pos[i,1] + final_vis_vectors[i,1],
                z=self.grid_pos[i,2] + final_vis_vectors[i,2]
            )
            marker.points = [start_pt, end_pt]
            
            marker.scale.x = 0.05
            marker.scale.y = 0.1
            marker.scale.z = 0.1
            
            marker.color = ColorRGBA(
                r=float(norm[i]),
                g=float(0.2 + 0.8 * (1.0 - norm[i])),
                b=1.0,
                a=0.8
            )
            
            marker_array.markers.append(marker)
            
        self.publisher_.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    node = RVizLiveFieldPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()