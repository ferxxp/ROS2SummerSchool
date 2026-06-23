import signal

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger


class Listener(Node):
    def __init__(self):
        super().__init__('listener')
        self.sub = None
        self.srv = self.create_service(Trigger, '/toggle_listener', self.toggle)
        self.get_logger().info('Listener started — subscribing OFF')

    def toggle(self, request, response):
        if self.sub:
            self.destroy_subscription(self.sub)
            self.sub = None
            self.get_logger().info('Subscribing OFF')
        else:
            self.sub = self.create_subscription(
                String, '/chatter', self.callback, 10
            )
            self.get_logger().info('Subscribing ON')
        response.success = True
        response.message = 'Toggled'
        return response

    def callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = Listener()

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
