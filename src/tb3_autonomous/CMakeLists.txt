cmake_minimum_required(VERSION 3.8)
project(tb3_autonomous)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch worlds maps config scripts
  DESTINATION share/${PROJECT_NAME})

# Executable helper (run with: ros2 run tb3_autonomous demo_goals.py)
install(PROGRAMS scripts/demo_goals.py
  DESTINATION lib/${PROJECT_NAME})

ament_package()
