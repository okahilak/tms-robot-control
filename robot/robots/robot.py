from abc import ABC, abstractmethod

class Robot(ABC):
    """
    Abstract base class for robot communication.

    This class defines the methods for interacting with a robot.
    """

    @abstractmethod
    def __init__(self, ip, config):
        """
        Initialize the robot connection.

        :param ip: The IP address of the robot.
        :param config: Configuration settings for the robot.
        """
        pass

    @abstractmethod
    def connect(self):
        """
        Connect to the robot.
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
        Disconnect the robot.
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        Check if the robot is connected.

        :return: True if connected, False otherwise.
        """
        pass

    @abstractmethod
    def initialize(self):
        """
        Initialize the robot settings.
        """
        pass

    @abstractmethod
    def get_pose(self):
        """
        Get the current pose of the robot, or None if the pose is not available.

        :return: The current pose. The pose is a list of 6 values: [x, y, z, rx, ry, rz].
          Return None if the pose is not available.
        """
        pass

    @abstractmethod
    def is_moving(self):
        """
        Return True if the robot is currently moving, False if it is not moving, and None if the
        information is not available.

        :return: True if the robot is moving, False if not moving, None if the information is not available.
        """
        pass

    @abstractmethod
    def is_error_state(self):
        """
        Return True if the robot is in an error state, False if it is not in an error state, and None if the
        information is not available.

        :return: True if in error state, False if not, and None if the information is not available.
        """
        pass

    @abstractmethod
    def read_force_sensor(self):
        """
        Read the force sensor's current value.

        :return: The force sensor reading.
        """
        pass

    @abstractmethod
    def move_linear(self, target, speed_ratio):
        """
        Move the robot in a linear path to the target in robot's base coordinate system with a given speed.

        If the robot is already moving, this method should stop the current movement and start the new one.

        :param target: The target position in a linear path.
        :param speed_ratio: The speed of the movement (as a proportion of the maximum speed; 0-1).
        """
        pass

    @abstractmethod
    def move_circular(self, start_position, waypoint, target, speed_ratio):
        """
        Move the robot in a circular path through a specified waypoint to the target in robot's base
        coordinate system with a given speed.

        If the robot is already moving, this method should stop the current movement and start the new one.

        :param start_position: The starting position of the robot.
        :param waypoint: The intermediate waypoint.
        :param target: The target position.
        :param speed_ratio: The speed of the movement (as a proportion of the maximum speed; 0-1).
        """
        pass

    @abstractmethod
    def stop_robot(self):
        """
        Stop the robot's movement.

        :return: True if the stop command was successful, False otherwise.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Perform necessary cleanup and disconnection procedures for the robot.
        """
        pass
