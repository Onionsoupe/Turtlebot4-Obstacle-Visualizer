import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy

qos = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10
)

class ObstacleVisualizer(Node):
    def __init__(self):
        super().__init__('obstacle_visualizer')

        # Subscriptions
        self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10)
        self.create_subscription(Image,'/oakd/rgb/preview/image_raw',self.image_callback , qos)
        self.create_subscription(CameraInfo, '/oakd/rgb/preview/camera_info', self.camera_info_callback, qos)

        # Publisher for fused image
        self.fused_image_pub = self.create_publisher(Image, '/obstacle_visualizer/fused_image', 10)

        # Latest data
        self.latest_scan = None
        self.camera_matrix = None
        self.dist_coeffs = None

        # CV bridge
        self.bridge = CvBridge()

        # GUI setup (optional)
        cv2.namedWindow("OAK-D Obstacle View", cv2.WINDOW_NORMAL)

        self.get_logger().info("Obstacle Visualizer Node Started — Publishing Fused Image")

    def lidar_callback(self, msg):
        self.latest_scan = msg

    def camera_info_callback(self, msg):
        self.camera_matrix = np.array(msg.k).reshape(3, 3)
        self.dist_coeffs = np.array(msg.d)

    def image_callback(self, msg):
        """
        Callback for the camera image.
        Publishes a fused image with LiDAR overlay if available.
        """

        try:
            # Convert ROS Image -> OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

            # Optional: draw a visible border for debugging
            cv2.rectangle(cv_image, (0, 0), (cv_image.shape[1]-1, cv_image.shape[0]-1), (0, 255, 0), 5)

            # Overlay LiDAR points if available
            if self.latest_scan is not None and self.camera_matrix is not None:
                fx, fy = self.camera_matrix[0, 0], self.camera_matrix[1, 1]
                cx, cy = self.camera_matrix[0, 2], self.camera_matrix[1, 2]

                ranges = np.array(self.latest_scan.ranges)
                angle_min = self.latest_scan.angle_min
                angle_increment = self.latest_scan.angle_increment

                for i, r in enumerate(ranges):
                    if np.isinf(r) or np.isnan(r) or r > 3.0:
                        continue

                    angle = angle_min + i * angle_increment
                    x = r * math.cos(angle)
                    y = r * math.sin(angle)
                    z = 1.0  # approximate height for visualization

                    u = int(fx * (-x) / z + cx)
                    v = int(fy * (y) / z + cy)

                    if 0 <= u < cv_image.shape[1] and 0 <= v < cv_image.shape[0]:
                        # Choose color based on distance
                        if r < 0.20:
                            color = (0, 0, 255)       # Red for very close
                        elif r < 0.30:
                            color = (0, 255, 255)     # Yellow for medium distance
                        else:
                            color = (0, 255, 0)       # Green for far points

                        cv2.circle(cv_image, (u, v), 3, color, -1)

            # Convert OpenCV image -> ROS Image message
            fused_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding='bgr8')
            fused_msg.header = msg.header  # keep same timestamp/frame_id

            # Publish the fused image
            self.fused_image_pub.publish(fused_msg)

            # Optional live display
            cv2.imshow("OAK-D Obstacle View", cv_image)
            cv2.waitKey(1)

            # Log once for debugging
            if not hasattr(self, 'has_logged'):
                self.get_logger().info("Publishing fused image (camera + LiDAR overlay)")
                self.has_logged = True

        except Exception as e:
            self.get_logger().error(f"Error in image_callback: {e}")




def main(args=None):
    rclpy.init(args=args)
    node = ObstacleVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
