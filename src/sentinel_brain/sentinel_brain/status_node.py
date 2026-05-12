import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

INITIAL_BATTERY = 100.0
BATTERY_DROP_PER_TICK = 3.0
TIMER_PERIOD = 1.0

class StatusNode(Node):
    def __init__(self):
        super().__init__('status_node')

        self.current_battery = INITIAL_BATTERY
        self.battery_publisher_ = self.create_publisher(Float32, 'battery_level', 10)

        self.timer = self.create_timer(TIMER_PERIOD, self.timer_callback)
        self.get_logger().info('StatusNode has been created!')

    def timer_callback(self):
        self.current_battery -= BATTERY_DROP_PER_TICK
        if self.current_battery < 0.0:
            self.current_battery = 0.0

        msg = Float32()
        msg.data = float(self.current_battery)
        self.battery_publisher_.publish(msg)

        self.get_logger().info(f"Sentinel System OK. Battery: {self.current_battery:.1f}")

def main(args=None):
    rclpy.init(args=args) # Start the ROS2 system

    node = StatusNode() # Create an instance of our node

    try:
        rclpy.spin(node) # Keep the node running until we shut it down
    except KeyboardInterrupt:
        pass # Handle Ctrl+C gracefully
    finally:
        node.destroy_node()
        rclpy.shutdown() # Clean up and shut down the ROS2 system
    
if __name__ == '__main__':
    StatusNode.main()