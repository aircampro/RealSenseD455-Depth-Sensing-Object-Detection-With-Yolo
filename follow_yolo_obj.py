#
# specify your yolo object to track check here for a list https://gist.github.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8
#
import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import os

# Set environment variables for ROS2 and TurtleBot3
os.environ['ROS_DOMAIN_ID'] = '55'
os.environ['TURTLEBOT3_MODEL'] = 'burger'

class GoToObjectNode(Node):
    def __init__(self, yolo_obj="dog"):
        super().__init__('go_to_obj_node')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.image_pub = self.create_publisher(Image, '/detected_object/image', 10)

        self.bridge = CvBridge()

        # Load the YOLOv11 model
        # Using the model file present in the workspace
        self.model = YOLO('yolo11s.pt')

        # Set up the RealSense D455 camera
        self.pipeline = rs.pipeline()
        config = rs.config()
        self.IMAGE_WIDTH = 640
        self.IMAGE_HEIGHT = 480
        config.enable_stream(rs.stream.color, self.IMAGE_WIDTH, self.IMAGE_HEIGHT, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, self.IMAGE_WIDTH, self.IMAGE_HEIGHT, rs.format.z16, 30)

        try:
            self.pipeline.start(config)
        except Exception as e:
            self.get_logger().error(f"Failed to start RealSense pipeline: {e}")
            return

        # Set the depth scale
        self.depth_scale = 0.001  # Default for D400 series is 1mm

        # Camera parameters for heading calculation
        self.IMAGE_CENTER_X = self.IMAGE_WIDTH // 2
        self.HORIZONTAL_FOV = 87  # degrees for RealSense D455

        # Control parameters
        self.target_class = yolo_obj
        self.stop_distance = 1  # meters
        self.linear_speed = 0.2
        self.angular_speed = 0.3
        self.center_tolerance = 50 # pixels

        # Timer for processing frames
        self.timer = self.create_timer(0.1, self.process_frame)  # 10Hz control loop

        self.get_logger().info('Go To Person Node Started')

    def process_frame(self):
        try:
            # Get the latest frame from the camera
            frames = self.pipeline.wait_for_frames(timeout_ms=100)
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()

            if not color_frame or not depth_frame:
                return

            # Convert the frames to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            # Detect objects using YOLO
            results = self.model(color_image, verbose=False)

            target_box = None
            target_distance = float('inf')
            target_center_x = 0

            # Process the results to find the closest person
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0].cpu().numpy())
                    class_name = self.model.names[class_id]

                    if class_name == self.target_class:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                        # Calculate distance
                        # Using median depth in the bounding box
                        # Clamp coordinates to image dimensions
                        x1 = max(0, x1)
                        y1 = max(0, y1)
                        x2 = min(self.IMAGE_WIDTH, x2)
                        y2 = min(self.IMAGE_HEIGHT, y2)

                        if x2 > x1 and y2 > y1:
                            depth_crop = depth_image[y1:y2, x1:x2]
                            if depth_crop.size > 0:
                                dist = np.median(depth_crop) * self.depth_scale

                                # Find the closest person
                                if dist < target_distance and dist > 0:
                                    target_distance = dist
                                    target_box = (x1, y1, x2, y2)
                                    target_center_x = (x1 + x2) // 2

            # Control Logic
            twist = Twist()

            if target_box:
                # Draw bounding box
                x1, y1, x2, y2 = target_box
                cv2.rectangle(color_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{self.target_class} {target_distance:.2f}m"
                cv2.putText(color_image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Navigation logic
                pixel_offset = self.IMAGE_CENTER_X - target_center_x

                # Rotation
                if abs(pixel_offset) > self.center_tolerance:
                    # Turn towards the object
                    # If object is to the left (center_x < image_center), pixel_offset is positive
                    # We need to turn left (positive angular velocity)
                    twist.angular.z = self.angular_speed * (1 if pixel_offset > 0 else -1)
                else:
                    # Centered, check distance
                    if target_distance > self.stop_distance:
                        twist.linear.x = self.linear_speed
                    else:
                        # Arrived
                        twist.linear.x = 0.0
                        twist.angular.z = 0.0
                        self.get_logger().info(f"Reached {self.target_class}!")
            else:
                # No person detected, spin slowly until one is found
                twist.angular.z = 0.2

            # Publish velocity command
            self.cmd_vel_pub.publish(twist)

            # Publish annotated image
            image_msg = self.bridge.cv2_to_imgmsg(color_image, encoding='bgr8')
            self.image_pub.publish(image_msg)

            # Optional: Show image locally if GUI is available
            # cv2.imshow("Robot View", color_image)
            # cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Error processing frame: {str(e)}')

    def destroy_node(self):
        self.pipeline.stop()
        cv2.destroyAllWindows()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = GoToObjectNode()                           # look for the dog

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
