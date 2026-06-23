import signal

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


class Talker(Node):
    def __init__(self):
        super().__init__('talker')
        self.pub = self.create_publisher(String, '/chatter', 10)
        self.timer = None
        self.counter = 0
        self.srv = self.create_service(Trigger, '/toggle_talker', self.toggle)
        self.get_logger().info('Talker started — publishing OFF')

    def toggle(self, request, response):
        if self.timer:
            self.timer.cancel()
            self.timer = None
            self.get_logger().info('Publishing OFF')
        else:
            self.timer = self.create_timer(1.0, self.publish)
            self.get_logger().info('Publishing ON')
        response.success = True
        response.message = 'Toggled'
        return response

    def publish(self):
        msg = String()
        msg.data = f'Hello ROS2 Summer School! #{self.counter}'
        self.pub.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = Talker()

    signal.signal(signal.SIGTERM, signal.default_int_handler)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
