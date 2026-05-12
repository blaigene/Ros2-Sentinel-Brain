import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from sentinel_interfaces.action import Patrol

import time

class PatrolActionServer(Node):
    def __init__(self):
        super().__init__('patrol_action_server')

        self._act_server = ActionServer(self,
            Patrol,
            'patrol',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)

        self.get_logger().info('Patrol Action Server has been created!')

    def goal_callback(self, goal_request):
        if (len(goal_request.waypoints_x) == 0 or len(goal_request.waypoints_y) == 0):
            self.get_logger().warn('Received patrol goal with empty waypoints')
            return GoalResponse.REJECT

        if (len(goal_request.waypoints_x) != len(goal_request.waypoints_y)):
            self.get_logger().warn('Received patrol goal with mismatched waypoint lengths')
            return GoalResponse.REJECT
        
        self.get_logger().info("Accepting goal...")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Received request to cancel patrol goal')
        return CancelResponse.ACCEPT
    
    def execute_callback(self, goal_handle):
        waypoints_x = goal_handle.request.waypoints_x
        waypoints_y = goal_handle.request.waypoints_y
        speed = max(0.1, goal_handle.request.speed)

        feedback = Patrol.Feedback()
        total = len(waypoints_x)
        for i, (x, y) in enumerate(zip(waypoints_x, waypoints_y)):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result = Patrol.Result()
                result.success = False
                result.message = 'Patrol canceled by user'
                return result
            
            self.get_logger().info(f'Moving to waypoint {i+1}/{total} at speed {speed}: ({x}, {y})')
            time.sleep(max(0.5, 2.0 / speed))

            feedback.current_waypoint = i + 1
            feedback.progress_percent = ((i + 1) / total) * 100
            goal_handle.publish_feedback(feedback)

        goal_handle.succeed()
        result = Patrol.Result()
        result.success = True
        result.message = 'Patrol completed successfully'
        return result

def main(args=None):
    rclpy.init(args=args)
    patrol_action_server = PatrolActionServer()
    executor = MultiThreadedExecutor()
    executor.add_node(patrol_action_server)
    executor.spin()
    patrol_action_server.destroy_node()
