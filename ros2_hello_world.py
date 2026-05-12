import rclpy 
from rclpy.node import Node

class HelloNode(Node):
	def __init__(self):
		super().__init__('hello_node')
		print(("Hello, ROS2!"))

def main():
	rclpy.init()
	node = HelloNode()
	rclpy.spin(node)
	node.destroy_node()
	rclpy.shutdown()

if __name__ == '__main__':
	main()
