#!/usr/bin/env python3
"""Send the robot through several goals in the obstacle arena using nav2_simple_commander.

Run after: simulation.launch.py + navigation.launch.py are up.
  ros2 run tb3_autonomous demo_goals.py
"""
import math

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

# (name, x, y, yaw) - all are free cells in obstacle_arena.world (purple floor markings)
GOALS = [
    ('A', 3.0, -4.0, 0.0),
    ('B', 3.8, 3.8, math.pi / 2),
    ('C', -3.5, 3.5, math.pi),
    ('E', -3.5, 0.0, -math.pi / 2),
    ('D', 0.0, -4.0, 0.0),
]
START = (-4.0, -4.0, 0.0)


def pose(nav, x, y, yaw):
    p = PoseStamped()
    p.header.frame_id = 'map'
    p.header.stamp = nav.get_clock().now().to_msg()
    p.pose.position.x, p.pose.position.y = x, y
    p.pose.orientation.z = math.sin(yaw / 2.0)
    p.pose.orientation.w = math.cos(yaw / 2.0)
    return p


def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.setInitialPose(pose(nav, *START))
    nav.waitUntilNav2Active()

    for name, x, y, yaw in GOALS:
        nav.get_logger().info(f'Going to goal {name} ({x:.1f}, {y:.1f})')
        nav.goToPose(pose(nav, x, y, yaw))
        while not nav.isTaskComplete():
            rclpy.spin_once(nav, timeout_sec=0.5)
        result = nav.getResult()
        status = {TaskResult.SUCCEEDED: 'reached', TaskResult.CANCELED: 'canceled',
                  TaskResult.FAILED: 'FAILED'}.get(result, 'unknown')
        nav.get_logger().info(f'Goal {name}: {status}')

    rclpy.shutdown()


if __name__ == '__main__':
    main()
