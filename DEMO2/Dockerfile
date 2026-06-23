FROM ros:jazzy

WORKDIR /ros2_ws
COPY ros2_ws/src src
RUN ../ros_entrypoint.sh && colcon build

RUN echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc
