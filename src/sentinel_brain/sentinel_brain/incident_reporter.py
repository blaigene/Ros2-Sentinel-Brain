import rclpy
from rclpy.node import Node
from sentinel_interfaces.srv import LogIncident

class IncidentReporter(Node):
    def __init__(self):
        super().__init__('incident_reporter')
        self.client = self.create_client(LogIncident, 'log_incident')
        
    def send_report(self, desc, sector):
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for server...')
        
        req = LogIncident.Request()
        req.description = desc
        req.sector_id = sector
        
        self.future = self.client.call_async(req)
        self.future.add_done_callback(self.response_callback)
        
    def response_callback(self, future):
        response = future.result()
        self.get_logger().info(f'Response:m{response.success}')
        
def main():
    rclpy.init()
    node = IncidentReporter()
    node.send_report('Security Breach', 3)
    rclpy.spin(node)
    rclpy.shutdown()