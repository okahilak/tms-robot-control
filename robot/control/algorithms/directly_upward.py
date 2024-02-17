from enum import Enum

import numpy as np

from robot.robots.axis import Axis
from robot.robots.direction import Direction


class MotionSequenceState(Enum):
    NOT_INITIATED = 0
    MOVE_UPWARD = 1
    MOVE_AND_ROTATE_IN_XY_PLANE = 2
    MOVE_DOWNWARD = 3
    FINISHED = 4

    def next(self):
        """Returns the next state in the sequence, and remains in the last state."""
        members = list(MotionSequenceState)
        index = members.index(self)

        # Check if current state is the last state
        if index == len(members) - 1:
            return self

        # Otherwise, proceed to the next state
        return members[index + 1]


class DirectlyUpwardAlgorithm:
    # Thresholds outside which a motion sequence is initiated.
    TRANSLATION_THRESHOLD = 10.0  # mm
    ROTATION_THRESHOLD = 5.0  # degrees

    UPWARD_MOVEMENT_TARGET_Z = 480.0  # mm from the robot basis

    # Ordered axes for the tuning motion: first rotation, then translation. This is the order
    # in which the displacement is received from neuronavigation.
    ORDERED_AXES = (Axis.RX, Axis.RY, Axis.RZ, Axis.X, Axis.Y, Axis.Z)

    # The threshold for both distance (in mm) and angle (in degrees) to move to the next axis
    # when performing tuning motion.
    DISTANCE_ANGLE_THRESHOLD = 1.0

    def __init__(self, robot, robot_config):
        self.robot = robot
        self.robot_config = robot_config

        self.reset()

    def reset(self):
        self.motion_sequence_state = MotionSequenceState.NOT_INITIATED

    def move_decision(self,
                      displacement_to_target,
                      target_pose_in_robot_space_estimated_from_head_pose,
                      target_pose_in_robot_space_estimated_from_displacement,
                      robot_pose,
                      head_center):

        # If motion sequence is not initiated, check if it should be.
        if self.motion_sequence_state == MotionSequenceState.NOT_INITIATED:

            # Compute the maximum translation and rotation to the target.
            max_translation = np.max(np.abs(displacement_to_target[:3]))
            max_rotation = np.max(np.abs(displacement_to_target[3:]))
            print("Max translation: {:.2f} mm, max rotation: {:.2f} degrees".format(max_translation, max_rotation))

            # If the maximum translation or rotation to the target is larger than the threshold, initiate the motion sequence.
            if max_translation > self.TRANSLATION_THRESHOLD or max_rotation > self.ROTATION_THRESHOLD:
                print("Initiating motion sequence")

                # Start the motion sequence by moving upward.
                self.motion_sequence_state = MotionSequenceState.MOVE_UPWARD

        # If motion sequence is initiated, continue the sequence, otherwise perform tuning motion.
        if self.motion_sequence_state != MotionSequenceState.NOT_INITIATED:
            success = self._perform_motion(target_pose_in_robot_space_estimated_from_displacement)
        else:
            success = self._tune(displacement_to_target)

        # If the motion sequence is finished, reset the state.
        if self.motion_sequence_state == MotionSequenceState.FINISHED:
            self.reset()

        # TODO: The force sensor is not normalized for now - add some logic here.
        normalize_force_sensor = False

        return success, normalize_force_sensor

    def _tune(self, displacement_to_target):
        print("Tuning")

        # Find the first axis with displacement larger than the threshold.
        axis_to_move = None
        for axis in self.ORDERED_AXES:
            axis_index = axis.value
            distance = np.abs(displacement_to_target[axis_index])
            direction = Direction.NEGATIVE if displacement_to_target[axis_index] < 0 else Direction.POSITIVE

            if distance > self.DISTANCE_ANGLE_THRESHOLD:
                axis_to_move = axis
                break

        # If none of the axes has a displacement larger than the threshold, return early.
        if axis_to_move is None:
            return False

        # Move along that axis.
        success = self.robot.move_linear_relative_to_tool_on_single_axis(
            axis=axis_to_move,
            direction=direction,
            distance=distance,
        )
        return success

    def _perform_motion(self, target_pose_in_robot_space):
        success = False

        if self.motion_sequence_state == MotionSequenceState.MOVE_UPWARD:
            print("Moving upward")

            pose = self.robot.get_coordinates()
            pose[2] = self.UPWARD_MOVEMENT_TARGET_Z
            success = self.robot.move_linear(pose)

        elif self.motion_sequence_state == MotionSequenceState.MOVE_AND_ROTATE_IN_XY_PLANE:
            print("Moving and rotating in XY plane")

            pose = target_pose_in_robot_space
            pose[2] = self.UPWARD_MOVEMENT_TARGET_Z
            success = self.robot.move_linear(pose)

        elif self.motion_sequence_state == MotionSequenceState.MOVE_DOWNWARD:
            print("Moving downward")

            pose = target_pose_in_robot_space
            success = self.robot.move_linear(pose)

        # Transition to the next state.
        self.motion_sequence_state = self.motion_sequence_state.next()

        return success