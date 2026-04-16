#
# ref:- https://github.com/bincent0929/RealSenseD455-Depth-Sensing-Object-Detection-With-Yolo/blob/main/README.md
# added diatance from center of the detection rectangles
#
import cv2
import numpy as np
import pyrealsense2 as rs
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('yolo11s.pt')

# Set up the RealSense D455 camera
pipeline = rs.pipeline()
config = rs.config()
IMAGE_WIDTH = 640
config.enable_stream(rs.stream.color, IMAGE_WIDTH, 480, rs.format.bgr8, 30)
# the rs.format.z16 is raw distance in millimeters
config.enable_stream(rs.stream.depth, IMAGE_WIDTH, 480, rs.format.z16, 30)
pipeline.start(config)

# Set the depth scale
# this value is used to convert the raw depth data from millimeters to meters
depth_scale = 0.0010000000474974513

# Camera parameters for heading calculation
IMAGE_CENTER_X = IMAGE_WIDTH // 2
HORIZONTAL_FOV = 87  # degrees for RealSense D455

# Create spatial and temporal filters for depth image
spatial = rs.spatial_filter()
temporal = rs.temporal_filter()

# Main loop
try:
    while True:
        # Get the latest frame from the camera
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            continue
        if not color_frame:
            continue				
        # Convert the frames to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Apply filters to depth image
        depth_frame = spatial.process(depth_frame)
        depth_frame = temporal.process(depth_frame)
        depth_image = np.asanyarray(depth_frame.get_data())

        # Convert the depth image to meters
        depth_image = depth_image * depth_scale

        # Detect objects using YOLOv8
        results = model(color_image)

        # Process the results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                confidence = box.conf[0].cpu().numpy()
                class_id = box.cls[0].cpu().numpy()

                if confidence < 0.5:
                    continue  # Skip detections with low confidence

                # Calculate the center of the bounding box
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                # Calculate heading (angle from camera center)
                # Positive angle = right, Negative angle = left
                pixel_offset = center_x - IMAGE_CENTER_X
                heading_angle = (pixel_offset / IMAGE_CENTER_X) * (HORIZONTAL_FOV / 2)

                # Calculate the distance to the object
                object_depth = np.median(depth_image[y1:y2, x1:x2])
                label = f"{object_depth:.2f}m, {heading_angle:.1f}°"

                # Draw a rectangle around the object
                cv2.rectangle(color_image, (x1, y1), (x2, y2), (252, 119, 30), 2)

                # Draw a circle at the center point
                cv2.circle(color_image, (center_x, center_y), 5, (0, 255, 0), -1)

                # calculate the distance for the bounding box center
                distance = depth_frame.get_distance(center_x, center_y)

                # Write the distances calculated to the screen
                cv2.putText(color_image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (252, 119, 30), 2)
                cv2.putText(color_image, distance, (x1, y1-20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 119, 252), 2)

                # Print the object's class, distance, heading, and center coordinates
                print(f"{model.names[int(class_id)]}: {object_depth:.2f}m at {heading_angle:.1f}° (center: {center_x}, {center_y})")

        # Show the image
        cv2.imshow("Color Image", color_image)
        cv2.waitKey(1)
finally:
    # Stop the pipeline
    pipeline.stop()
    cv2.destroyAllWindows()
