import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3

import numpy as np
import matplotlib.pyplot as plt
import time


class FFTNode(Node):
    def __init__(self):
        super().__init__('fft_node')

        self.sub = self.create_subscription(
            Vector3,
            'telemetry',
            self.callback,
            10
        )

        self.start_time = time.time()
        self.duration = 10.0  # seconds

        self.data = []
        self.timestamps = []

        self.get_logger().info("Collecting data for 10 seconds...")

    def callback(self, msg):
        now = time.time()

        if now - self.start_time > self.duration:
            self.process_fft()
            rclpy.shutdown()
            return

        # collect one axis (choose x for now)
        self.data.append(msg.x)
        self.timestamps.append(now)

    def process_fft(self):
        self.get_logger().info("Processing FFT...")

        if len(self.data) < 10:
            print("Not enough data")
            return

        data = np.array(self.data)

        # estimate sampling rate
        dt = np.mean(np.diff(self.timestamps))
        fs = 1.0 / dt

        # remove DC offset
        data = data - np.mean(data)

        # FFT
        fft_vals = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(data), d=dt)

        # take positive half
        mask = freqs > 0
        freqs = freqs[mask]
        fft_vals = np.abs(fft_vals[mask])

        # plot
        plt.figure()
        plt.plot(freqs, fft_vals)
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.title("FFT of Bx (10s window)")
        plt.grid()
        plt.show()


def main():
    rclpy.init()
    node = FFTNode()
    rclpy.spin(node)


if __name__ == '__main__':
    main()