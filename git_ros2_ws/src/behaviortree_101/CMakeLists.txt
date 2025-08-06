cmake_minimum_required(VERSION 3.8)
project(behaviortree_101)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(rclcpp REQUIRED)
find_package(behaviortree_cpp REQUIRED)

add_executable(bt_node
  src/bt_all_in_one.cpp
)

ament_target_dependencies(bt_node
  rclcpp
  behaviortree_cpp
)

install(TARGETS
  bt_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()