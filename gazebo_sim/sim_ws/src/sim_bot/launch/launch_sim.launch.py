# import os
# from ament_index_python.packages import get_package_share_directory
# from launch import LaunchDescription
# from launch.actions import IncludeLaunchDescription
# from launch.launch_description_sources import PythonLaunchDescriptionSource

# from launch_ros.actions import Node
# import xacro


# def generate_launch_description():


#     name_package = 'sim_bot'

#     # Robot
#     robot_name = 'diff_drive_robot'
#     model_file_relative_path = 'description/robot.urdf.xacro'
#     model_file_path = os.path.join(get_package_share_directory(name_package), model_file_relative_path)

#     # World
    
    
#     robot_descroption = xacro.process_file(model_file_path).toxml()

#     gazebo_ros_pakage_launch = PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('ros_gz_sim'),
#                                                                             'launch', 'gz_sim.launch.py', ))

#     gazebo = IncludeLaunchDescription(
#         gazebo_ros_pakage_launch,
#         launch_arguments={'gz_args': ['-r -v -v4 empty.sdf'], 'on_exit_shutdown': 'true'}.items()
#     )


#     # Gazebo Node
#     node_gazebo_spawn = Node(
#     	package='ros_gz_sim', 
#     	executable='create',
# 		arguments=[
#             '-topic', 'robot_description',
#             '-name', robot_name,
#         ],
# 		output='screen',
# 	)

#     # Robot State Publisher Node
#     node_state_publisher = Node(
#     	package='robot_state_publisher', 
#     	executable='robot_state_publisher',
# 		output='screen',
# 		parameters=[{
#             'robot_description': robot_descroption,
#             'use_sim_time': True,
#         }],
# 	)

#     # Bridge params Node
#     bridge_params = os.path.join(
#         get_package_share_directory(name_package),
#         'config',
#         'bridge_parameters.yaml',
#     )

#     start_gazebo_ros_bridge_cmd = Node(
#      	package='ros_gz_bridge', 
#     	executable='parameter_bridge',
# 		arguments=[
#             '--ros-args',
#             '-p',
#             f'config_file:={bridge_params}',
#         ],
# 		output='screen',       
#     )

#     launch_description_object = LaunchDescription()
#     launch_description_object.add_action(gazebo_ros_pakage_launch)
#     launch_description_object.add_action(node_gazebo_spawn)
#     launch_description_object.add_action(node_state_publisher)
#     launch_description_object.add_action(start_gazebo_ros_bridge_cmd)

#     return launch_description_object

import os
import xacro
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # Define the robot's name and package name
    robot_name = "diff_drive_robot"
    robot_pkg_name = "sim_bot"

    # Define a launch argument for the world file, defaulting to "empty.sdf"
    world_arg = DeclareLaunchArgument(
        'world',
        default_value='empty.sdf',
        description='Specify the world file for Gazebo (e.g., empty.sdf)'
    )

    # Define launch arguments for initial pose
    x_arg = DeclareLaunchArgument(
        'x', default_value='0.0', description='Initial X position')

    y_arg = DeclareLaunchArgument(
        'y', default_value='0.0', description='Initial Y position')

    z_arg = DeclareLaunchArgument(
        'z', default_value='0.5', description='Initial Z position')

    roll_arg = DeclareLaunchArgument(
        'R', default_value='0.0', description='Initial Roll')

    pitch_arg = DeclareLaunchArgument(
        'P', default_value='0.0', description='Initial Pitch')

    yaw_arg = DeclareLaunchArgument(
        'Y', default_value='0.0', description='Initial Yaw')

    # Retrieve launch configurations
    world_file = LaunchConfiguration('world')
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    roll = LaunchConfiguration('R')
    pitch = LaunchConfiguration('P')
    yaw = LaunchConfiguration('Y')

    # Set paths to Xacro model and configuration files
    robot_model_path = os.path.join(
        get_package_share_directory(robot_pkg_name),
        'description',
        'robot.urdf.xacro'
    )

    gz_bridge_params_path = os.path.join(
        get_package_share_directory(robot_pkg_name),
        'config',
        'gz_bridge.yaml'
    )

    # Process the Xacro file to generate the URDF representation of the robot
    robot_description = xacro.process_file(robot_model_path).toxml()

    # Prepare to include the Gazebo simulation launch file
    gazebo_pkg_launch = PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory('ros_gz_sim'),
            'launch',
            'gz_sim.launch.py'
        )
    )

    # Include the Gazebo launch description with specific arguments
    gazebo_launch = IncludeLaunchDescription(
        gazebo_pkg_launch,
        launch_arguments={
            'gz_args': [f'-r -v 4 ', world_file],
            'on_exit_shutdown': 'true'
        }.items()
    )

    # Create a node to spawn the robot model in the Gazebo environment
    spawn_model_gazebo_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robot_name,
            '-string', robot_description,
            '-x', x,
            '-y', y,
            '-z', z,
            '-R', roll,
            '-P', pitch,
            '-Y', yaw,
            '-allow_renaming', 'false'
        ],
        output='screen',
    )

    # Create a node to publish the robot's state based on its URDF description
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description, 'use_sim_time': True}
        ],
        output='screen'
    )

    # Create a node for the ROS-Gazebo bridge to handle message passing
    gz_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args', '-p',
            f'config_file:={gz_bridge_params_path}'
        ],
        output='screen'
    )

    return LaunchDescription([
        world_arg,
        gazebo_launch,
        x_arg,
        y_arg,
        z_arg,
        roll_arg,
        pitch_arg,
        yaw_arg,
        spawn_model_gazebo_node,
        robot_state_publisher_node,
        gz_bridge_node,
    ])
