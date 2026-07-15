cmake_minimum_required(VERSION 3.5)
project(agv_autonomy)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(action_msgs REQUIRED)

# 1. Install python module package (agv_autonomy python structure)
install(DIRECTORY agv_autonomy/
  DESTINATION local/lib/python3.10/dist-packages/agv_autonomy
  FILES_MATCHING PATTERN "*.py"
)

# 2. Install executable python scripts to lib/agv_autonomy
install(PROGRAMS
  agv_autonomy/agv_behavior_tree.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME agv_behavior_tree
)

# 3. Share directories (launch, worlds, models, rviz, config)
install(DIRECTORY
  launch
  worlds
  models
  rviz
  config
  DESTINATION share/${PROJECT_NAME}
)

# 4. Generate custom action interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/PlayAudio.action"
  DEPENDENCIES builtin_interfaces
)

# Export dependencies
ament_export_dependencies(rosidl_default_runtime)

# Wrap package
ament_package()
