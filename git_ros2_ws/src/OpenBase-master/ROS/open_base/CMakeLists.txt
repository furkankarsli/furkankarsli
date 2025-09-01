cmake_minimum_required(VERSION 3.8)
project(open_base)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(gazebo_ros2_control REQUIRED)
find_package(ros2_control REQUIRED)
find_package(ros2_controllers REQUIRED)

find_package(rosidl_default_generators REQUIRED)

# Find Eigen3
find_package(PkgConfig)
pkg_search_module(Eigen3 REQUIRED eigen3)

# Generate messages and services
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Velocity.msg"
  "msg/MovementBezier.msg"
  "msg/MovementGeneric.msg"
  "msg/Movement.msg"
  "srv/FrameToFrame.srv"
  "srv/KinematicsForward.srv"
  "srv/KinematicsInverse.srv"
  DEPENDENCIES std_msgs geometry_msgs
)

# Include directories
include_directories(include
  ${Eigen3_INCLUDE_DIRS}
)

# Create executables - only main for now
# add_executable(${PROJECT_NAME}_kinematics src/kinematics.cpp)
# ament_target_dependencies(${PROJECT_NAME}_kinematics
#   rclcpp
#   std_msgs
#   geometry_msgs
#   sensor_msgs
# )

# add_executable(${PROJECT_NAME}_odometry src/odometry.cpp)
# ament_target_dependencies(${PROJECT_NAME}_odometry
#   rclcpp
#   std_msgs
#   geometry_msgs
#   sensor_msgs
# )

# add_executable(${PROJECT_NAME}_sensor_encoder src/sensor/encoder.cpp)
# ament_target_dependencies(${PROJECT_NAME}_sensor_encoder
#   rclcpp
#   std_msgs
#   sensor_msgs
# )

# Original main controller disabled to avoid conflicts
# add_executable(${PROJECT_NAME}_main src/main_ros2.cpp)
# ament_target_dependencies(${PROJECT_NAME}_main
#   rclcpp
#   std_msgs
#   geometry_msgs
#   sensor_msgs
# )
# rosidl_target_interfaces(${PROJECT_NAME}_main ${PROJECT_NAME} "rosidl_typesupport_cpp")

# Simple wheel controller
add_executable(simple_wheel_controller src/simple_wheel_controller.cpp)
ament_target_dependencies(simple_wheel_controller
  rclcpp
  geometry_msgs
)

# Install targets
install(TARGETS
  simple_wheel_controller
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY
  launch
  config
  urdf
  xacro
  mesh
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
