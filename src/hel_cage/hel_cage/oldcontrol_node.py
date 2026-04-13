import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from std_msgs.msg import String
import numpy as np

# ==========================================
# 1. THE CONTROLLER INTERFACE
# ==========================================
class BaseController:
    """All future controllers must inherit this to guarantee they have these methods."""
    def compute(self, target: np.ndarray, current: np.ndarray, dt: float, base_pwm: np.ndarray) -> tuple:
        raise NotImplementedError
    
    def reset(self):
        raise NotImplementedError

# ==========================================
# 2. YOUR PID STRATEGY
# ==========================================
class PIDController(BaseController):
    def __init__(self):
        # Gains
        self.kp = 0.2
        self.ki = 0.0
        self.kd = 0.0
        
        # State arrays (handles X, Y, Z simultaneously)
        self.integral = np.zeros(3)
        self.prev_error = np.zeros(3)
        self.deriv = np.zeros(3)
        
        # Parameters
        self.alpha = 0.2
        self.deadband = 0.5

    def update_gains(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

    def reset(self):
        """Clears memory (called when a new target is received)"""
        self.integral.fill(0.0)
        self.prev_error.fill(0.0)
        self.deriv.fill(0.0)

    def compute(self, target: np.ndarray, current: np.ndarray, dt: float, base_pwm: np.ndarray) -> tuple:
        # Calculate error for all 3 axes
        error = target - current

        # DEADBAND: Force error to 0 if within threshold
        error[np.abs(error) < self.deadband] = 0.0

        # INTEGRAL: Add error with anti-windup clamping (-100 to 100)
        self.integral = np.clip(self.integral + (error * dt), -100.0, 100.0)

        # DERIVATIVE: Filtered derivative
        self.deriv = self.alpha * ((error - self.prev_error) / dt) + (1 - self.alpha) * self.deriv
        self.prev_error = error.copy() # Store for next loop

        # PID OUTPUT
        pid_out = (self.kp * error) + (self.ki * self.integral) + (self.kd * self.deriv)

        # FINAL OUTPUT: Add base and clamp to PWM limits
        final_out = np.clip(base_pwm + pid_out, -255.0, 255.0)

        return error, final_out

# ==========================================
# 3. THE ROS 2 NODE (Wraps the controller)
# ==========================================
class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')

        # ===== LOAD CONTROLLER =====
        # To change control strategies later, just change this one line:
        # self.controller = SomeOtherAdvancedController()
        self.controller = PIDController()

        # ===== SUBS =====
        self.create_subscription(Vector3, 'telemetry',    self.tel_cb,  10)
        self.create_subscription(Vector3, 'cmd_B',        self.cmd_cb,  10)
        self.create_subscription(String,  'control_cmd',  self.ctrl_cb, 10)
        self.create_subscription(Vector3, 'pid_gain',     self.pid_cb,  10)
        self.create_subscription(Vector3, 'pwm_base',     self.base_cb, 10)

        # ===== PUBS =====
        self.pwm_pub   = self.create_publisher(Vector3, 'pwm_cmd', 10)
        self.error_pub = self.create_publisher(Vector3, 'error',   10)

        # ===== STATE =====
        # Using numpy arrays natively makes passing data to the controller easier
        self.target  = np.zeros(3)
        self.current = np.zeros(3)
        self.pwm_base = np.zeros(3)
        self.control_enabled = False

        # ===== TIMING =====
        self.last_time = self.get_clock().now()
        self.last_log  = self.get_clock().now()

        self.create_timer(0.02, self.control_loop)

    # ===== CALLBACKS =====
    def tel_cb(self, msg: Vector3):
        self.current = np.array([msg.x, msg.y, msg.z])

    def cmd_cb(self, msg: Vector3):
        self.target = np.array([msg.x, msg.y, msg.z])
        self.controller.reset() # Reset the controller memory on new command

    def pid_cb(self, msg: Vector3):
        if hasattr(self.controller, 'update_gains'):
            self.controller.update_gains(msg.x, msg.y, msg.z)

    def base_cb(self, msg: Vector3):
        self.pwm_base = np.array([msg.x, msg.y, msg.z])

    def ctrl_cb(self, msg: String):
        cmd = msg.data.strip().upper()
        if cmd == 'START':
            self.control_enabled = True
            self.last_time = self.get_clock().now()
        elif cmd == 'STOP':
            self.control_enabled = False
            zero = Vector3()
            self.pwm_pub.publish(zero)

    # ===== CONTROL LOOP =====
    def control_loop(self):
        if not self.control_enabled:
            return

        now = self.get_clock().now()
        dt  = (now - self.last_time).nanoseconds * 1e-9
        self.last_time = now

        if dt <= 0:
            return
        dt = min(dt, 0.02)

        # --- EXECUTE THE MODULAR CONTROL STRATEGY ---
        error, pwm_out = self.controller.compute(self.target, self.current, dt, self.pwm_base)

        # Publish error
        err_msg = Vector3(x=float(error[0]), y=float(error[1]), z=float(error[2]))
        self.error_pub.publish(err_msg)

        # Publish PWM
        out_msg = Vector3(x=float(pwm_out[0]), y=float(pwm_out[1]), z=float(pwm_out[2]))
        self.pwm_pub.publish(out_msg)

        # Logging
        if (now - self.last_log).nanoseconds > 200_000_000:
            self.get_logger().info(
                f'ERR: {error[0]:.2f},{error[1]:.2f},{error[2]:.2f} | PWM: {pwm_out[0]:.2f},{pwm_out[1]:.2f},{pwm_out[2]:.2f}'
            )
            self.last_log = now

def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()