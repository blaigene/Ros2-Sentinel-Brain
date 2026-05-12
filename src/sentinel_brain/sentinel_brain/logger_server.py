import rclpy
from rclpy.node import Node
from sentinel_interfaces.srv import LogIncident

class LoggerServer(Node):
    def __init__(self):
        super().__init__('logger_server')

        # Create the service: Type, Name, Callback
        self.srv = self.create_service(LogIncident, 'log_incident', self.log_callback)
        self.get_logger().info('Sentinel Logger Server is active...')

    def log_callback(self, request, response):
        self.get_logger().info(f'NEW INCIDENT: {request.description} in Sector {request.sector_id}')

        # Logic: Mark as successful and provide dummy ID
        response.success = True
        response.incident_id = f"ID-{request.sector_id}-99"
        return response

def main():
    rclpy.init()
    node = LoggerServer()
    rclpy.spin(node)
    rclpy.shutdown()