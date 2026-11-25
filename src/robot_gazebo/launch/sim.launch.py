import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    desc = get_package_share_directory('robot_description')
    sim = get_package_share_directory('robot_gazebo')
    ros_gz = get_package_share_directory('ros_gz_sim')

    xacro_file = os.path.join(desc, 'urdf', 'robot.urdf.xacro')
    robot_description = ParameterValue(Command(['xacro ', xacro_file]), value_type=str)
    world = os.path.join(sim, 'worlds', 'piece.sdf')
    bridge_cfg = os.path.join(sim, 'config', 'bridge.yaml')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(ros_gz, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': f'-r {world}'}.items())

    rsp = Node(package='robot_state_publisher', executable='robot_state_publisher',
               parameters=[{'robot_description': robot_description, 'use_sim_time': True}])

    spawn = Node(package='ros_gz_sim', executable='create',
                 arguments=['-topic', 'robot_description', '-name', 'mon_robot', '-z', '0.05'])

    bridge = Node(package='ros_gz_bridge', executable='parameter_bridge',
                  parameters=[{'config_file': bridge_cfg, 'use_sim_time': True}])

    return LaunchDescription([gazebo, rsp, spawn, bridge])