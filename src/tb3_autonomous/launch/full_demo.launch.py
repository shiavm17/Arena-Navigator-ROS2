"""One-command launcher: simulation + (mapping | navigation).

  ros2 launch tb3_autonomous full_demo.launch.py mode:=mapping
  ros2 launch tb3_autonomous full_demo.launch.py mode:=navigation
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import LaunchConfigurationEquals
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg = get_package_share_directory('tb3_autonomous')

    def include(name, **kw):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', name)), **kw)

    sim = include('simulation.launch.py',
                  launch_arguments={'gui': LaunchConfiguration('gui')}.items())
    mapping = include('mapping.launch.py', condition=LaunchConfigurationEquals('mode', 'mapping'))
    navigation = include('navigation.launch.py',
                         launch_arguments={'map': LaunchConfiguration('map')}.items(),
                         condition=LaunchConfigurationEquals('mode', 'navigation'))

    return LaunchDescription([
        DeclareLaunchArgument('mode', default_value='mapping', description='mapping | navigation'),
        DeclareLaunchArgument('gui', default_value='true'),
        DeclareLaunchArgument('map', default_value=os.path.join(pkg, 'maps', 'obstacle_arena.yaml')),
        sim,
        # give Gazebo ~6 s to spawn the robot and start /clock, /scan, TF
        TimerAction(period=6.0, actions=[mapping, navigation]),
    ])
