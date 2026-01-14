# Base: Standard Ubuntu 22.04 (no GPU required for development)
FROM ubuntu:22.04

# Prevent interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux

# Set locale
RUN apt-get update && apt-get install -y \
    locales \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Install essential build tools and utilities
RUN apt-get update && apt-get install -y \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    gnupg2 \
    lsb-release \
    git \
    vim \
    nano \
    build-essential \
    cmake \
    pkg-config \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# ROS2 Humble Installation
# ==========================================
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
    | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt-get update && apt-get install -y \
    ros-humble-ros-base \
    ros-humble-cv-bridge \
    ros-humble-sensor-msgs \
    ros-humble-geometry-msgs \
    ros-humble-nav-msgs \
    ros-humble-rmw-cyclonedds-cpp \
    python3-colcon-common-extensions \
    python3-rosdep \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep
RUN rosdep init || true \
    && rosdep update

# ==========================================
# Intel RealSense SDK Installation (headers only for LSP)
# ==========================================
# Install RealSense development libraries for code completion
# Note: This provides headers and libs but won't connect to actual hardware
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE \
    || apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE

RUN add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u

RUN apt-get update && apt-get install -y \
    librealsense2-dev \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Python Dependencies (CPU-only for LSP support)
# ==========================================
# Upgrade pip
RUN python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch CPU-only (for YOLOv8) - lightweight for development
RUN pip3 install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install pyrealsense2
RUN pip3 install --no-cache-dir pyrealsense2

# Install ultralytics (YOLOv8/v11)
RUN pip3 install --no-cache-dir ultralytics

# Install additional Python packages
RUN pip3 install --no-cache-dir \
    opencv-python \
    numpy \
    matplotlib

# ==========================================
# User Setup
# ==========================================
ARG USERNAME=ros
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update && apt-get install -y sudo \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && rm -rf /var/lib/apt/lists/*

# ==========================================
# Workspace Setup
# ==========================================
WORKDIR /workspace

# Source ROS2 setup in bashrc for the user
RUN echo "source /opt/ros/humble/setup.bash" >> /home/$USERNAME/.bashrc \
    && echo "export ROS_DOMAIN_ID=55" >> /home/$USERNAME/.bashrc \
    && echo "export TURTLEBOT3_MODEL=burger" >> /home/$USERNAME/.bashrc \
    && echo "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp" >> /home/$USERNAME/.bashrc

# Switch to user
USER $USERNAME

# Default command
CMD ["/bin/bash"]
