# RealSense Depth Sensing Object Detection with YOLO11
## What The Programs Do
- [turtlebot3_move_forward.py](https://github.com/bincent0929/RealSenseD455-Depth-Sensing-Object-Detection-With-Yolov8/blob/main/turtlebot3_move_forward.py "turtlebot3_move_forward.py")
	- Use this to test that your host can connect to your robot and initiate actions.
- [realsense_with_yolo11.py](https://github.com/bincent0929/RealSenseD455-Depth-Sensing-Object-Detection-With-Yolov8/blob/main/realsense_with_yolo11.py "realsense_with_yolo11.py")
	- Use this to make sure your Realsense camera is properly connecting to your host and working with `yolo` to detect objects and detect their distance.
- [follow_person_node.py](https://github.com/bincent0929/RealSenseD455-Depth-Sensing-Object-Detection-With-Yolov8/blob/main/follow_person_node.py "follow_person_node.py")
	- Set to initialize a connection to a Robotis robot running ROS2 with a Realsense camera mounted that runs Ultralytics's YOLO to detect person's in the environment and follow them until reaching a meter away from them.
 -  [follow_yolo_obj.py](https://github.com/bincent0929/RealSenseD455-Depth-Sensing-Object-Detection-With-Yolov8/blob/main/follow_person_node.py "follow_yolo_obj.py")
	- Set to initialize a connection to a Robotis robot running ROS2 with a Realsense camera mounted that runs Ultralytics's YOLO to detect the specified yolo object in the environment and follow them until reaching a meter away from them.
## How To Set Up Your Environment To Run The Programs
Firstly, you need to make sure that the robot is able to be reached using the normal process of connecting to it from Robotis. You want to make sure that you have a PC setup by following [this guide](https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/#pc-setup) (during the ROS2 install step, you DO NOT need to install any more than the `ros-humble-ros-base` for ROS). Then get an SBC that is connected to the robot of your choice's motors through an OpenCR board or equivalent by following [this guide](https://emanual.robotis.com/docs/en/platform/turtlebot3/sbc_setup/#sbc-setup).
***
After you get all the ROS2 and Robotis packages onto your robot and host PC, you'll want to go ahead and set up a virtual environment on your host PC to download the Python libraries that will allow you to pull data from the depth camera and detect objects from the RGB data from the camera. 

!!!You don't need to worry about installing libraries for controlling your robot through `pip` like `rclpy` because those were already installed when you set up ROS2 on your Robotis robot!!!

Before you get into downloading the packages through `pip`, it's best to set up `uv`. Check out what `uv` exactly is [here](https://github.com/astral-sh/uv). It's basically just a better implementation of `pip`, but the only reason I require it is because I've found that `pip` will just straight up fail with `ultralytics[export]` on certain devices (specifically on the Jetson).

Now, when you want to download a `pip` library, just do it like this (and I'll use `ultralytics[export]` as the package here):
```
uv pip install ultralytics[export]
```
***
## !!!!Before you set this up with anything, go ahead and set up a Python virtual environment to download python packages/libraries into in the same directory that you cloned this repository into!!!!
### How To Set This Up For An Nvidia Jetson Host
#### 1. BEFORE ANYTHING, MAKE SURE YOU HAVE THE CORRECT `Jetpack` VERSION ACCORDING TO THE REQUIREMENTS OF YOUR LIBRARIES/PACKAGES
As of Dec. 15 2025, for getting this working, the limitation comes from `librealsense` for versioning of `Jetpack` for your Jetson to get this working.

Whatever the guide says [here](https://github.com/realsenseai/librealsense/blob/master/doc/installation_jetson.md) for your board is what you want to **ENSURE** that you have installed.

At the moment it says, "The method was verified with **Jetson AGX Thor™** with JetPack 7.0 (beta level), **Jetson AGX Orin™** with JetPack 6.0, **Jetson AGX Xavier™** boards with JetPack **5.0.2**\[L4T 35.1.0\]."

For example, for the case of a Jetson Orin Nano Developer Kit to install the native backend, you'll want to install `Jetpack 6.0` onto your Jetson to make sure it the packages build correctly.
#### 2. For installing `librealsense` and `pyrealsense2`
From [this guide](https://github.com/realsenseai/librealsense/blob/master/doc/installation_jetson.md) follow the native backend guide steps.

When you reach "**Build librealsense2 SDK**", make sure you download all the dependencies at the beginning of [the Ubuntu installation guide](https://github.com/realsenseai/librealsense/blob/master/doc/installation.md) that they point you to.

As long as this build completes, you should be good to plug in your camera and see that it works with the `realsense-viewer`.

If it does work, go ahead and enter your Python virtual environment and run `uv pip install pyrealsense2`.
#### 3. For installing `ultralytics`/`yolo`
Follow [this](https://docs.ultralytics.com/guides/nvidia-jetson/#install-ultralytics-package_1) to get it installed.

Make sure you do `uv pip install ultralytics[export]`! Or it may get hung up.

And make sure that you follow everything in the guide, or your camera will process frames SIGNIFICANTLY slower than it could.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Heads up, the guide has you install `torch` and `torchvision` that don't support `Jetpack 6.0`!

Use these instead when you reach that step (they are just the previous versions of the `.whl` files that they tell you to use in the guide):
[correct torch wheel from ultralytics](https://github.com/ultralytics/assets/releases/download/v0.0.0/torch-2.3.0-cp310-cp310-linux_aarch64.whl)
[correct torchvision wheel from ultralytics](https://github.com/ultralytics/assets/releases/download/v0.0.0/torchvision-0.18.0a0+6043bc2-cp310-cp310-linux_aarch64.whl)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Make sure to try and run `python3 yolo` one time and make sure it provides you with feedback that it has been installed.
### How To Set This Up For An AMD64/x86 Host
#### 1. Make sure you have Ubuntu 22.04 installed and updated all the way and that you have followed the ROS2 PC set up outlined above.
#### 2. For installing `librealsense` and `pyrealsense2`
Just follow [this](https://github.com/realsenseai/librealsense/blob/master/doc/distribution_linux.md) and it will get you all the packages your computer will need, no building necessary.

Do a `realsense-viewer` test to make sure your camera connects.

If it works, go ahead and enter your Python virtual environment and run `uv pip install pyrealsense2`.
#### 3. For installing `ultralytics`/`yolo`
All you have to do to set this up is to just run a sweet `uv pip install ultralytics[export]` in the Python virtual environment you set up and once it's done, run `python3 yolo`, and if it says its installed, you're all good.
***
