#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

class PatrolWorker(Node):
    def __init__(self):
        super().__init__('patrol_worker')
        
        # 1) DECLARE parmeters (The Contract)
        self.declare_parameter('patrol_speed', 0.5)
        self.declare_parameter('waypoints', [0.0, 0.0])
        
        # 2) GET parameters
        self.speed = float(self.get_parameter('patrol_speed').value)
        self.points = self.get_parameter('waypoints').value
        
        self.current_index = 0
        
        self.get_logger().info(f"Patrol started! Speed: {self.speed} m/s")
        self.get_logger().info(f"Waypoints raw: {self.points}")
        
        # Timer period shows the effect of speed
        self.period = max(0.5, 2.0 / max(self.speed, 1e-6))
        self.timer = self.create_timer(self.period, self.patrol_callback)
    
    def patrol_callback(self):
        # Expect at least one (x, y) pair
        if len(self.points) < 2 or len(self.points) % 2 != 0:
            self.get_logger().warn("Waypoints parameter is invalid. It should be a list of (x, y) pairs.")
            return
        
        # Patrol finished
        if self.current_index >= len(self.points):
            self.get_logger().info("Patrol completed! Robot stopped.")
            return
        
        x = self.points[self.current_index]
        y = self.points[self.current_index + 1]
        
        self.get_logger().info(f"Moving to: ({x}, {y}) at {self.speed} m/s")
        self.current_index += 2
        
def main():
    rclpy.init()
    patrol_worker = PatrolWorker()
    rclpy.spin(patrol_worker)
    patrol_worker.destroy_node()
    rclpy.shutdown()