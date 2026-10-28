"""Nav2 (map_server + AMCL + planner/controller/BT) + RViz2 on a saved map.
Start simulation.launch.py first (same world, same spawn pose used while mapping).

  ros2 launch tb3_autonomous navigation.launch.py
  ros2 launch tb3_autonomous navigation.launch.py map:=/abs/path/to/my_map.yaml
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('tb3_autonomous')
    nav2_bringup = get_package_share_directory('nav2_bringup')
    use_sim_time = LaunchConfiguration('use_sim_time')

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': use_sim_time,
            'autostart': 'true',
            'slam': 'False',
        }.items())

    rviz = Node(
        package='rviz2', executable='rviz2', name='rviz2', output='screen',
        arguments=['-d', os.path.join(pkg, 'config', 'rviz_navigation.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(LaunchConfiguration('rviz')))

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('map', default_value=os.path.join(pkg, 'maps', 'obstacle_arena.yaml')),
        DeclareLaunchArgument('params_file', default_value=os.path.join(pkg, 'config', 'nav2_params.yaml')),
        nav2, rviz])
