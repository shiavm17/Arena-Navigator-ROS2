#!/usr/bin/env bash
# Quick health check. Run while simulation / mapping / navigation is running.
# Usage: ./check_system.sh
source /opt/ros/humble/setup.bash 2>/dev/null
ok(){ echo "  [OK]   $*"; }; bad(){ echo "  [FAIL] $*"; }

echo "== Environment =="
[ "${ROS_DISTRO}" = "humble" ] && ok "ROS_DISTRO=humble" || bad "ROS_DISTRO=${ROS_DISTRO:-unset} (need humble)"
[ -n "$TURTLEBOT3_MODEL" ] && ok "TURTLEBOT3_MODEL=$TURTLEBOT3_MODEL" || bad "TURTLEBOT3_MODEL not set (export TURTLEBOT3_MODEL=burger)"

echo "== Packages =="
for p in tb3_autonomous turtlebot3_gazebo turtlebot3_teleop slam_toolbox nav2_bringup nav2_map_server gazebo_ros rviz2; do
  ros2 pkg prefix "$p" >/dev/null 2>&1 && ok "$p" || bad "$p missing"
done

echo "== Topics =="
TOPICS="$(ros2 topic list 2>/dev/null)"
for t in /clock /scan /odom /tf /tf_static /cmd_vel /robot_description; do
  echo "$TOPICS" | grep -qx "$t" && ok "$t" || bad "$t not found"
done
echo "$TOPICS" | grep -qx "/map" && ok "/map (SLAM or map_server running)" || echo "  [INFO] /map not present"

echo "== Data flowing (3 s each) =="
for t in /scan /odom /clock; do
  timeout 4 ros2 topic hz "$t" --window 5 2>/dev/null | head -n 2 | tail -n 1 | sed "s|^|  $t: |" || true
done

echo "== TF chain =="
timeout 4 ros2 run tf2_ros tf2_echo odom base_footprint 2>/dev/null | head -n 4 || bad "odom -> base_footprint missing"
timeout 4 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | head -n 4 || echo "  [INFO] map -> odom missing (normal before SLAM/AMCL starts)"

echo "== Nav2 lifecycle states =="
for n in map_server amcl controller_server planner_server behavior_server bt_navigator; do
  s="$(ros2 lifecycle get /$n 2>/dev/null)"
  [ -n "$s" ] && echo "  $n: $s" || echo "  $n: (not running)"
done
