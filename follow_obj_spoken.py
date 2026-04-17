# -*- coding: utf-8 -*-
#
# specify your yolo object to track check here for a list https://gist.github.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8
# with speach recognition and voice
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
import sys
import subprocess
# pip install speechrecognition
#
import speech_recognition as sr
import time

# ============= choose speach engine ===================
#Espeak for windows or Linux
#https://espeak.sourceforge.net/
#$ sudo apt-get install espeak
#
#Voices for say on MacOS
#Alex                en_US    # Most people recognize me by my voice.
#Alice               it_IT    # Salve, mi chiamo Alice e sono una voce italiana.
#Allison             en_US    # Hello, my name is Allison. I am an American-English voice.
#Alva                sv_SE    # Hej, jag heter Alva. Jag är en svensk röst.
#Amelie              fr_CA    # Bonjour, je m’appelle Amelie. Je suis une voix canadienne.
#Anna                de_DE    # Hallo, ich heiße Anna und ich bin eine deutsche Stimme.
#Carmit              he_IL    # שלום. קוראים לי כרמית, ואני קול בשפה העברית

# get the platform to branch on the voice to use 
plat=sys.platform
#│ Linux               │ linux or linux2 (*) │
#│ Windows             │ win32               │
#│ Windows/Cygwin      │ cygwin              │
#│ Windows/MSYS2       │ msys                │
#│ Mac OS X            │ darwin              │
#│ OS/2                │ os2                 │
#│ OS/2 EMX            │ os2emx              │
#│ RiscOS              │ riscos              │
#│ AtheOS              │ atheos              │
#│ FreeBSD 7           │ freebsd7            │
#│ FreeBSD 8           │ freebsd8            │
#│ FreeBSD N           │ freebsdN            │
#│ OpenBSD 6           │ openbsd6            │
#│ AIX                 │ aix (**)

def pronounce_msg(msg, v="Allison"):
    voice = v
    text = msg
    if not plat.find("darwin") == -1:
        command = ['say', '-v', f'{voice}', f'{text}']
        cp = subprocess.run(command)
    else:
        cp = subprocess.check_output(["espeak", "-k5", "-s150", text])	
    return cp

# list of yolo object detection classes
# ref:- https://gist.github.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8
yolo_obj_classes={
  "class": {
    "0": "person",
    "1": "bicycle",
    "2": "car",
    "3": "motorcycle",
    "4": "airplane",
    "5": "bus",
    "6": "train",
    "7": "truck",
    "8": "boat",
    "9": "traffic light",
    "10": "fire hydrant",
    "11": "stop sign",
    "12": "parking meter",
    "13": "bench",
    "14": "bird",
    "15": "cat",
    "16": "dog",
    "17": "horse",
    "18": "sheep",
    "19": "cow",
    "20": "elephant",
    "21": "bear",
    "22": "zebra",
    "23": "giraffe",
    "24": "backpack",
    "25": "umbrella",
    "26": "handbag",
    "27": "tie",
    "28": "suitcase",
    "29": "frisbee",
    "30": "skis",
    "31": "snowboard",
    "32": "sports ball",
    "33": "kite",
    "34": "baseball bat",
    "35": "baseball glove",
    "36": "skateboard",
    "37": "surfboard",
    "38": "tennis racket",
    "39": "bottle",
    "40": "wine glass",
    "41": "cup",
    "42": "fork",
    "43": "knife",
    "44": "spoon",
    "45": "bowl",
    "46": "banana",
    "47": "apple",
    "48": "sandwich",
    "49": "orange",
    "50": "brocolli",
    "51": "carrot",
    "52": "hot dog",
    "53": "pizza",
    "54": "donut",
    "55": "cake",
    "56": "chair",
    "57": "couch",
    "58": "potted plant",
    "59": "bed",
    "60": "dining table",
    "61": "toilet",
    "62": "tv",
    "63": "laptop",
    "64": "mouse",
    "65": "remote",
    "66": "keyboard",
    "67": "cell phone",
    "68": "microwave",
    "69": "oven",
    "70": "toaster",
    "71": "sink",
    "72": "refrigerator",
    "73": "book",
    "74": "clock",
    "75": "vase",
    "76": "scissors",
    "77": "teddy bear",
    "78": "hair drier",
    "79": "toothbrush"
  }
}

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please choose the class to follow...")
        pronounce_msg("Please choose the class to follow...")		
        audio_data = recognizer.listen(source)
        print("Processing...")
    try:
        text = recognizer.recognize_google(audio_data, language='en-US')                # can change e.g. ja-JP
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

def ask_what_to_track():
    loop_success = False
	if loop_success == False:
        recognized_text = recognize_speech_from_mic()
        print(f"you said {recognized_text}")
        pronounce_msg(f"you said {recognized_text}")
        for k in yolo_obj_classes['class'].values():
            if k == recognized_text:
		        loop_success = True
        pronounce_msg(f"could not match your speach with a valid yolo class say again please")
		time.sleep(1)
        pronounce_msg(f"say the class you want to follow again please")
		time.sleep(1)
        pronounce_msg("the name only")
    pronounce_msg(f"following the {recognized_text}")
    return recognized_text

# Set environment variables for ROS2 and TurtleBot3
os.environ['ROS_DOMAIN_ID'] = '55'
os.environ['TURTLEBOT3_MODEL'] = 'burger'
SPIN_AMT=0.2                                                                   # spin when nothing was found
DIST_MSG_DUR=10.0                                                              # how often to call distance to object

class GoToObjectNode(Node):
    def __init__(self, yolo_obj="dog"):
        super().__init__('go_to_obj_node')

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.image_pub = self.create_publisher(Image, '/detected_object/image', 10)
        self.start_tm = time.time()
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
        self.timer = self.create_timer(0.1, self.process_frame)                                             # 10Hz control loop

        self.get_logger().info('Go To Object Node Started')

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

            # Process the results to find the closest object
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

                                # Find the closest object
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
                label = f"{self.target_class} {target_distance:.2f} meters"
                cv2.putText(color_image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                if label is not None and ((time.time() - self.start_tm) > DIST_MSG_DUR):
                    pronounce_msg(label)
                    self.start_tm = time.time()
					
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
                # No object detected, spin slowly until one is found
                twist.angular.z = SPIN_AMT

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
    look_for_class=ask_what_to_track()                              # ask the user what to look for ?
    node = GoToObjectNode(look_for_class)                           # look for the class requested by the users voice
    try:
        rclpy.spin(node)                                            # run ROS2 node
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
