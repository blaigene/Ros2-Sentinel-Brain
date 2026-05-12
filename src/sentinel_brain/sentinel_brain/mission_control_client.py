import os
import time
import threading

import yaml
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String, Float32
from ament_index_python.packages import get_package_share_directory
from sentinel_interfaces.action import Patrol

class MissionControl(Node):
    def __init__(self):
        super().__init__('mission_control_client')

        self.inspection_period_sec = self.declare_parameter('inspection_period_sec', 10.0).value
        self.patrol_speed = self.declare_parameter('patrol_speed', 0.8).value
        self.low_battery_threshold = self.declare_parameter('low_battery_threshold', 30.0).value
        self.minimum_battery_at_start = self.declare_parameter('minimum_battery_at_start', 60.0).value
        self.mission_file = self.declare_parameter('mission_file', '').value

        self.battery_level = None
        self.goal_done_event = threading.Event()
        self.running = True
        self.at_home = False
        self.current_point_name = None

        self.mission_status_publisher_ = self.create_publisher(String, 'mission_status', 10)
        self.battery_subscription_ = self.create_subscription(Float32, 'battery_level', self.battery_callback, 10)

        self._act_client = ActionClient(self, Patrol, 'patrol')

        self.mission_name = 'unknown_mission'
        self.home_name = 'home'
        self.home_point = (0.0, 0.0)
        self.inspection_points = []

        self.load_mission_file()

        self.control_thread = threading.Thread(target=self.control_loop, daemon=True)
        self.control_thread.start()

    def load_mission_file(self):
        if not self.mission_file:
            self.get_logger().warn('Mission file parameter is empty')
            self.publish_status('No mission file configured')
            return

        file_path = os.path.expanduser(self.mission_file)
        if not os.path.isfile(file_path):
            package_share = get_package_share_directory('sentinel_brain')
            alt_path = os.path.join(package_share, self.mission_file)
            if os.path.isfile(alt_path):
                file_path = alt_path

        if not os.path.isfile(file_path):
            self.get_logger().error(f'Mission file not found: {self.mission_file}')
            self.publish_status('Mission file missing')
            return

        try:
            with open(file_path, 'r') as yaml_file:
                data = yaml.safe_load(yaml_file) or {}
        except Exception as exc:
            self.get_logger().error(f'Failed to load mission file: {exc}')
            self.publish_status('Failed to load mission file')
            return

        self.mission_name = data.get('mission_name', 'unknown_mission')
        home_data = data.get('home', {})
        self.home_name = 'home'
        self.home_point = (0.0, 0.0)

        if isinstance(home_data, dict):
            self.home_name = home_data.get('name', 'home')
            position = home_data.get('position', [0.0, 0.0])
        elif isinstance(home_data, (list, tuple)) and len(home_data) >= 2:
            position = home_data
        else:
            position = [0.0, 0.0]

        try:
            self.home_point = (float(position[0]), float(position[1]))
        except (ValueError, TypeError, IndexError):
            self.home_point = (0.0, 0.0)

        raw_points = data.get('inspection_points', [])
        self.inspection_points = []
        if isinstance(raw_points, list):
            for index, item in enumerate(raw_points):
                point_name = f'point_{index + 1}'
                point_position = [0.0, 0.0]

                if isinstance(item, dict):
                    point_name = item.get('name', point_name)
                    point_position = item.get('position', [0.0, 0.0])
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    point_position = item
                else:
                    continue

                try:
                    point_position = (float(point_position[0]), float(point_position[1]))
                    self.inspection_points.append({
                        'name': str(point_name),
                        'position': point_position
                    })
                except (ValueError, TypeError, IndexError):
                    continue

        self.get_logger().info(f'Loaded mission "{self.mission_name}" with {len(self.inspection_points)} inspection points')
        self.publish_status(f'Mission loaded: {self.mission_name}')

    def battery_callback(self, msg):
        self.battery_level = float(msg.data)
        self.get_logger().info(f'Received battery level: {self.battery_level:.1f}%')

    def publish_status(self, status_text):
        msg = String()
        msg.data = status_text
        self.mission_status_publisher_.publish(msg)
        self.get_logger().info(f'Mission status: {status_text}')

    def send_patrol_goal(self, x, y, name=None):
        self.get_logger().info('Waiting for patrol action server...')
        if not self._act_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Patrol action server unavailable')
            self.publish_status('Patrol server unavailable')
            return False

        if name is not None:
            self.current_point_name = name

        goal_msg = Patrol.Goal()
        goal_msg.waypoints_x = [float(x)]
        goal_msg.waypoints_y = [float(y)]
        goal_msg.speed = float(self.patrol_speed)

        self.at_home = False
        self.get_logger().info(f"Sending waypoint '{self.current_point_name}' to PatrolWorker: ({x:.2f}, {y:.2f})")
        send_goal_future = self._act_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        send_goal_future.add_done_callback(self.goal_response_callback)
        return True

    def feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        feedback = type('FeedbackProxy', (), {})()
        feedback.current_waypoint = fb.current_waypoint
        feedback.progress = fb.progress_percent
        self.get_logger().info(f"inspect_{self.current_point_name}: waypoint={feedback.current_waypoint}, progress={feedback.progress}%")

    def goal_response_callback(self, future):
        try:
            goal_handle = future.result()
        except Exception as exc:
            self.get_logger().error(f'Goal response failed: {exc}')
            self.goal_done_event.set()
            return

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            self.goal_done_event.set()
            return

        self.get_logger().info('Goal accepted')
        self.current_goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        try:
            result = future.result().result
            self.get_logger().info(f"Job 'inspect_{self.current_point_name}' completed: Patrol Completed!")
            self.publish_status(f'Result: {result.message}')
        except Exception as exc:
            self.get_logger().error(f'Failed to get result: {exc}')
            self.publish_status('Goal result error')
        finally:
            self.goal_done_event.set()

    def go_home(self):
        if self.home_point is None:
            self.get_logger().warn('Home point is not configured')
            return

        self.publish_status(f'Returning to home: {self.home_name}')
        if self.at_home:
            self.get_logger().info('Already at home, will wait at dock')
            return

        self.goal_done_event.clear()
        if not self.send_patrol_goal(self.home_point[0], self.home_point[1]):
            return

        self.wait_for_goal_done()
        self.at_home = True

    def wait_for_goal_done(self):
        while rclpy.ok() and self.running and not self.goal_done_event.is_set():
            time.sleep(0.1)

    def wait_period(self, seconds):
        end_time = time.time() + float(seconds)
        while rclpy.ok() and self.running and time.time() < end_time:
            time.sleep(0.2)

    def control_loop(self):
        while rclpy.ok() and self.running:
            if self.battery_level is None:
                self.publish_status('Waiting for battery status')
                time.sleep(0.5)
                continue

            if self.battery_level <= self.low_battery_threshold:
                if not self.at_home:
                    self.publish_status('Battery below low threshold, returning home')
                    self.go_home()
                else:
                    self.publish_status('Battery low at home, waiting at dock')
                self.get_logger().info(f"Waiting {self.inspection_period_sec} seconds before next inspection cycle.")
                self.wait_period(self.inspection_period_sec)
                continue

            if self.battery_level < self.minimum_battery_at_start:
                if not self.at_home:
                    self.publish_status('Battery too low to start inspection, returning home')
                    self.go_home()
                else:
                    self.publish_status('Battery too low at home to start inspection')
                self.get_logger().info(f"Waiting {self.inspection_period_sec} seconds before next inspection cycle.")
                self.wait_period(self.inspection_period_sec)
                continue

            if not self.inspection_points:
                self.publish_status('No inspection points available')
                time.sleep(1.0)
                continue

            self.at_home = False
            self.publish_status('Starting inspection cycle')
            completed_cycle = True

            for point in self.inspection_points:
                if not rclpy.ok() or not self.running:
                    completed_cycle = False
                    break

                if self.battery_level < self.low_battery_threshold:
                    self.publish_status('Battery too low during inspection')
                    completed_cycle = False
                    break

                self.current_point_name = point['name']
                self.get_logger().info(f"Inspecting {self.current_point_name}. Battery: {self.battery_level:.1f}%")
                self.goal_done_event.clear()
                if not self.send_patrol_goal(point['position'][0], point['position'][1], name=self.current_point_name):
                    completed_cycle = False
                    break

                self.wait_for_goal_done()

                if self.battery_level < self.low_battery_threshold:
                    self.publish_status('Battery dropped below threshold after waypoint')
                    completed_cycle = False
                    break

            if not rclpy.ok() or not self.running:
                break

            if self.battery_level < self.low_battery_threshold:
                self.go_home()
                self.get_logger().info(f"Waiting {self.inspection_period_sec} seconds before next inspection cycle.")
                self.wait_period(self.inspection_period_sec)
                continue

            if completed_cycle:
                self.publish_status('Inspection cycle complete')
                self.get_logger().info('Inspection cycle finished.')
                self.get_logger().info(f"Waiting {self.inspection_period_sec} seconds before next inspection cycle.")
                self.wait_period(self.inspection_period_sec)

        self.publish_status('Mission control thread stopping')

    def stop(self):
        self.running = False
        self.goal_done_event.set()


def main(args=None):
    rclpy.init(args=args)
    node = MissionControl()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Mission control shutdown requested')
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
