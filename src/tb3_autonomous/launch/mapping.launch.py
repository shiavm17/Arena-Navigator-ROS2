"""SLAM Toolbox (online async) + RViz2 for mapping. Start simulation.launch.py first.

  ros2 launch tb3_autonomous mapping.launch.py
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('tb3_autonomous')
    use_sim_time = LaunchConfiguration('use_sim_time')

    slam = Node(
        package='slam_toolbox', executable='async_slam_toolbox_node', name='slam_toolbox',
        output='screen',
        parameters=[LaunchConfiguration('slam_params_file'), {'use_sim_time': use_sim_time}])

    rviz = Node(
        package='rviz2', executable='rviz2', name='rviz2', output='screen',
        arguments=['-d', os.path.join(pkg, 'config', 'rviz_mapping.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(LaunchConfiguration('rviz')))

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('slam_params_file',
                              default_value=os.path.join(pkg, 'config', 'slam_params.yaml')),
        slam, rviz])
