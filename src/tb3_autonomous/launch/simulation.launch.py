"""Gazebo Classic + custom obstacle arena + TurtleBot3 (default: burger).

Usage:
  ros2 launch tb3_autonomous simulation.launch.py
  ros2 launch tb3_autonomous simulation.launch.py gui:=false x_pose:=-4.0 y_pose:=-4.0 yaw:=0.0
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('tb3_autonomous')
    gazebo_ros = get_package_share_directory('gazebo_ros')
    tb3_gazebo = get_package_share_directory('turtlebot3_gazebo')

    model = os.environ.get('TURTLEBOT3_MODEL', 'burger')
    world = os.path.join(pkg, 'worlds', 'obstacle_arena.world')
    sdf = os.path.join(tb3_gazebo, 'models', f'turtlebot3_{model}', 'model.sdf')

    # Make TurtleBot3 meshes/models resolvable and stop Gazebo querying the online model DB.
    models_path = os.path.join(tb3_gazebo, 'models')
    existing = os.environ.get('GAZEBO_MODEL_PATH', '')
    gazebo_model_path = models_path + (os.pathsep + existing if existing else '')

    use_sim_time = LaunchConfiguration('use_sim_time')

    args = [
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('gui', default_value='true', description='Start gzclient'),
        DeclareLaunchArgument('x_pose', default_value='-4.0'),
        DeclareLaunchArgument('y_pose', default_value='-4.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
    ]

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros, 'launch', 'gzserver.launch.py')),
        launch_arguments={'world': world}.items())

    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gazebo_ros, 'launch', 'gzclient.launch.py')),
        condition=IfCondition(LaunchConfiguration('gui')))

    # Publishes /robot_description and robot TF tree (base_footprint -> base_link -> sensors).
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(tb3_gazebo, 'launch', 'robot_state_publisher.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items())

    # The SDF carries the diff-drive (/cmd_vel, /odom, odom TF), LiDAR (/scan) and IMU plugins.
    spawn = Node(
        package='gazebo_ros', executable='spawn_entity.py', output='screen',
        arguments=['-entity', model, '-file', sdf,
                   '-x', LaunchConfiguration('x_pose'),
                   '-y', LaunchConfiguration('y_pose'),
                   '-z', '0.01',
                   '-Y', LaunchConfiguration('yaw')])

    return LaunchDescription([
        SetEnvironmentVariable('GAZEBO_MODEL_PATH', gazebo_model_path),
        SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', ''),
        *args, gzserver, gzclient, rsp, spawn])
