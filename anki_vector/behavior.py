# Copyright (c) 2018 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. _behavior:

Behavior related classes and functions.

Behaviors represent a complex task which requires Vector's
internal logic to determine how long it will take. This
may include combinations of animation, path planning or
other functionality. Examples include :meth:`drive_on_charger`,
:meth:`set_lift_height`, etc.

For commands such as :meth:`go_to_pose`, :meth:`drive_on_charger` and :meth:`dock_with_cube`,
Vector uses path planning, which refers to the problem of
navigating the robot from point A to B without collisions. Vector
loads known obstacles from his map, creates a path to navigate
around those objects, then starts following the path. If a new obstacle
is found while following the path, a new plan may be created.

The :class:`BehaviorComponent` class in this module contains
functions for all the behaviors.
"""

__all__ = ["BehaviorComponent", "MAX_HEAD_ANGLE", "MAX_LIFT_HEIGHT", "MAX_LIFT_HEIGHT_MM",
           "MIN_HEAD_ANGLE", "MIN_LIFT_HEIGHT", "MIN_LIFT_HEIGHT_MM"]


from . import connection, objects, util
from .messaging import protocol
from .exceptions import VectorException
from typing import Union

# Constants

#: The minimum angle the robot's head can be set to
# TODO Clamp to this value.
MIN_HEAD_ANGLE = util.degrees(-22)

#: The maximum angle the robot's head can be set to
# TODO Clamp to this value.
MAX_HEAD_ANGLE = util.degrees(45)

# The lowest height-above-ground that lift can be moved to in millimeters.
MIN_LIFT_HEIGHT_MM = 32.0

#: The lowest height-above-ground that lift can be moved to
MIN_LIFT_HEIGHT = util.distance_mm(MIN_LIFT_HEIGHT_MM)

# The largest height-above-ground that lift can be moved to in millimeters.
MAX_LIFT_HEIGHT_MM = 92.0

#: The largest height-above-ground that lift can be moved to
MAX_LIFT_HEIGHT = util.distance_mm(MAX_LIFT_HEIGHT_MM)


class BehaviorComponent(util.Component):
    """Run behaviors on Vector"""

    _next_action_id = protocol.FIRST_SDK_TAG

    def __init__(self, robot):
        super().__init__(robot)
        self._current_priority = None
        self._is_active = False

        self._motion_profile_map = {}

    # TODO Make the motion_profile_map into a class.
    @property
    def motion_profile_map(self) -> dict:
        """Tells Vector how to drive when receiving navigation and movement actions
        such as go_to_pose and dock_with_cube.

        motion_prof_map values are as follows:
         |  speed_mmps (float)
         |  accel_mmps2 (float)
         |  decel_mmps2 (float)
         |  point_turn_speed_rad_per_sec (float)
         |  point_turn_accel_rad_per_sec2 (float)
         |  point_turn_decel_rad_per_sec2 (float)
         |  dock_speed_mmps (float)
         |  dock_accel_mmps2 (float)
         |  dock_decel_mmps2 (float)
         |  reverse_speed_mmps (float)
         |  is_custom (bool)

        :getter: Returns the motion profile map
        :setter: Sets the motion profile map

        :param motion_prof_map: Provide custom speed, acceleration and deceleration
            values with which the robot goes to the given pose.
        """
        return self._motion_profile_map

    @motion_profile_map.setter
    def motion_profile_map(self, motion_profile_map: dict):
        self._motion_profile_map = motion_profile_map

    def _motion_profile_for_proto(self) -> protocol.PathMotionProfile:
        """Packages the current motion profile into a proto object

        Returns:
            A profile object describing motion which can be passed with any proto action message.
        """
        # TODO: This should be made into its own class
        default_motion_profile = {
            "speed_mmps": 100.0,
            "accel_mmps2": 200.0,
            "decel_mmps2": 500.0,
            "point_turn_speed_rad_per_sec": 2.0,
            "point_turn_accel_rad_per_sec2": 10.0,
            "point_turn_decel_rad_per_sec2": 10.0,
            "dock_speed_mmps": 60.0,
            "dock_accel_mmps2": 200.0,
            "dock_decel_mmps2": 500.0,
            "reverse_speed_mmps": 80.0,
            "is_custom": 1 if self._motion_profile_map else 0
        }
        default_motion_profile.update(self._motion_profile_map)

        return protocol.PathMotionProfile(**default_motion_profile)

    # @property
    # def current_priority(self):
    #    # TODO implement
    #    return self._current_priority

    # @property
    # def is_active(self) -> bool:
    #    # TODO implement
    #    """True if the behavior is currently active and may run on the robot."""
    #    return self._is_active

    @classmethod
    def _get_next_action_id(cls):
        # Post increment _current_action_id (and loop within the SDK_TAG range)
        next_action_id = cls._next_action_id
        if cls._next_action_id == protocol.LAST_SDK_TAG:
            cls._next_action_id = protocol.FIRST_SDK_TAG
        else:
            cls._next_action_id += 1
        return next_action_id

    # Navigation actions
    @connection.on_connection_thread()
    async def drive_off_charger(self):
        """Drive Vector off the charger

        If Vector is on the charger, drives him off the charger.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.behavior.drive_off_charger()
        """
        drive_off_charger_request = protocol.DriveOffChargerRequest()
        return await self.grpc_interface.DriveOffCharger(drive_off_charger_request)

    @connection.on_connection_thread()
    async def drive_on_charger(self):
        """Drive Vector onto the charger

        Vector will attempt to find the charger and, if successful, he will
        back onto it and start charging.

        Vector's charger has a visual marker so that the robot can locate it
        for self-docking.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.behavior.drive_on_charger()
        """
        drive_on_charger_request = protocol.DriveOnChargerRequest()
        return await self.grpc_interface.DriveOnCharger(drive_on_charger_request)

    # TODO Make this cancellable with is_cancellable_behavior
    @connection.on_connection_thread()
    async def find_faces(self) -> protocol.FindFacesResponse:
        """Look around for faces

        Turn in place and move head to look for faces

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.behavior.find_faces()
        """
        find_faces_request = protocol.FindFacesRequest()
        return await self.grpc_interface.FindFaces(find_faces_request)

    # TODO Make this cancellable with is_cancellable_behavior
    @connection.on_connection_thread()
    async def look_around_in_place(self) -> protocol.LookAroundInPlaceResponse:
        """Look around in place

        Turn in place and move head to see what's around Vector

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.behavior.look_around_in_place()
        """
        look_around_in_place_request = protocol.LookAroundInPlaceRequest()
        return await self.grpc_interface.LookAroundInPlace(look_around_in_place_request)

    # TODO Make this cancellable with is_cancellable_behavior
    @connection.on_connection_thread()
    async def roll_visible_cube(self) -> protocol.RollBlockResponse:
        """Roll a cube that is currently known to the robot

        This behavior will move into position as necessary based on relative
        distance and orientation.

        Vector needs to see the block for this to succeed.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.behavior.roll_visible_cube()
        """
        roll_block_request = protocol.RollBlockRequest()
        return await self.grpc_interface.RollBlock(roll_block_request)

    # TODO Make this cancellable with is_cancellable_behavior
    @connection.on_connection_thread()
    async def say_text(self, text: str, use_vector_voice: bool = True,
                       duration_scalar: float = 1.0) -> protocol.SayTextResponse:
        """Make Vector speak text.

        .. testcode::

            import anki_vector
            with anki_vector.Robot() as robot:
                robot.behavior.say_text("Hello World")

        :param text: The words for Vector to say.
        :param use_vector_voice: Whether to use Vector's robot voice
                (otherwise, he uses a generic human male voice).
        :param duration_scalar: Adjust the relative duration of the
                generated text to speech audio.

        :return: object that provides the status and utterance state
        """
        say_text_request = protocol.SayTextRequest(text=text,
                                                   use_vector_voice=use_vector_voice,
                                                   duration_scalar=duration_scalar)
        return await self.conn.grpc_interface.SayText(say_text_request)

    def say_localized_text(self, text: str, use_vector_voice: bool = True, duration_scalar: float = 1.0,
                           language: str = 'en') -> protocol.SayTextResponse:
        """Make Vector speak text with a different localized voice.

                .. testcode::

                    import anki_vector
                    with anki_vector.Robot() as robot:
                        robot.behavior.say_localized_text("Hello World",language="de")

        :param text: The words for Vector to say.
        :param use_vector_voice: Whether to use Vector's robot voice
                (otherwise, he uses a generic human male voice).
        :param duration_scalar: Adjust the relative duration of the
                generated text to speech audio.
        :param language: Adjust the language spoken for this text

            possible values:
                - de:         German
                - en:         English
                - ja or jp:   Japanese
                - fr:         French

        :return: object that provides the status and utterance state
        """

        if language == 'en':
            locale = 'en_US'
        if language == 'de':
            locale = 'de_DE'
        elif language == 'fr':
            locale = 'fr_FR'
        elif language == 'ja' or language == 'jp':
            locale = 'ja_JP'
            duration_scalar = duration_scalar / 3
        else:
            locale = language

        if self.robot.force_async:
            # @TODO: make sure requests are sent in conjunction when say_future would be returned -
            #  currently it's blocking async, to ensure the language is switched back after talking
            #  because otherwise the persisted different locale would lead to failed cloud requests,
            #  as on english seems to be supported right now and vector would show network-error on his screen
            self.change_locale(locale=locale).result()
            say_future = self.say_text(text, use_vector_voice, duration_scalar)
            res = say_future.result()
            self.change_locale(locale='en_US').result()
            return res
        else:
            self.change_locale(locale=locale)
            say_future = self.say_text(text, use_vector_voice, duration_scalar)
            self.change_locale(locale='en_US')
        return say_future

    # TODO Make this cancellable with is_cancellable_behavior
    @connection.on_connection_thread(requires_control=False)
    async def app_intent(self, intent: str, param: Union[str, int] = None) -> protocol.AppIntentResponse:
        """Send Vector an intention to do something.

        .. testcode::

            import anki_vector
            with anki_vector.Robot(behavior_control_level=None) as robot:
                robot.behavior.app_intent(intent='intent_system_sleep')

        :param intent: The intention key
        :param param: Intention parameter, usually a json encoded string or an int of secounds for the clock timer

        :return: object that provides the status
        """

        # clock timer uses the length of `param` as the number of seconds to set the timer for
        if intent=='intent_clock_settimer' and type(param) == int:
            param = 'x' * param

        app_intent_request = protocol.AppIntentRequest(intent=intent, param=param)
        return await self.conn.grpc_interface.AppIntent(app_intent_request)

    # TODO Make this cancellable with is_cancellable_behavior
    @connection.on_connection_thread()
    async def change_locale(self, locale: str) -> protocol.UpdateSettingsResponse:
        """Change Vectors voice locale

        .. testcode::

            import anki_vector
            with anki_vector.Robot() as robot:
                robot.behavior.change_locale(locale='de_DE')

        :param locale: The locale ISO code

        :return: object that provides the status
        """

        settings = {'locale': locale}
        updatet_settings_request = protocol.UpdateSettingsRequest(settings=settings)
        return await self.conn.grpc_interface.UpdateSettings(updatet_settings_request)

    # TODO Make this cancellable with is_cancellable_behavior
    @connection.on_connection_thread()
    async def update_settings(self, settings) -> protocol.UpdateSettingsResponse:
        """Send Vector an intention to do something.

        .. testcode::

            import anki_vector
            with anki_vector.Robot() as robot:
                robot.behavior.update_settings(settings={'locale':'en_US'})

        :param settings: A list object with the following keys
            clock_24_hour: bool
            eye_color: EyeColor
            default_location: string,
            dist_is_metric: bool
            locale: string
            master_volume: Volume
            temp_is_fahrenheit: bool
            time_zone: string
            button_wakeword: ButtonWakeWord

        :return: object that provides the status
        """
        updatet_settings_request = protocol.UpdateSettingsRequest(settings=settings)
        return await self.conn.grpc_interface.UpdateSettings(updatet_settings_request)

    # TODO Make this cancellable with is_cancellable_behavior?
    @connection.on_connection_thread()
    async def set_eye_color(self, hue: float, saturation: float) -> protocol.SetEyeColorResponse:
        """Set Vector's eye color.

        .. testcode::

            import anki_vector
            import time

            with anki_vector.Robot() as robot:
                print("Set Vector's eye color to purple...")
                robot.behavior.set_eye_color(0.83, 0.76)
                time.sleep(5)

        :param hue: The hue to use for Vector's eyes.
        :param saturation: The saturation to use for Vector's eyes.
        """
        eye_color_request = protocol.SetEyeColorRequest(hue=hue, saturation=saturation)
        return await self.conn.grpc_interface.SetEyeColor(eye_color_request)

    @connection.on_connection_thread()
    async def go_to_pose(self,
                         pose: util.Pose,
                         relative_to_robot: bool = False,
                         num_retries: int = 0) -> protocol.GoToPoseResponse:
        """Tells Vector to drive to the specified pose and orientation.

        In navigating to the requested pose, Vector will use path planning.

        If relative_to_robot is set to True, the given pose will assume the
        robot's pose as its origin.

        Since the robot understands position by monitoring its tread movement,
        it does not understand movement in the z axis. This means that the only
        applicable elements of pose in this situation are position.x position.y
        and rotation.angle_z.

        :param pose: The destination pose.
        :param relative_to_robot: Whether the given pose is relative to
                                  the robot's pose.
        :param num_retries: Number of times to re-attempt action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                pose = anki_vector.util.Pose(x=50, y=0, z=0, angle_z=anki_vector.util.Angle(degrees=0))
                robot.behavior.go_to_pose(pose)
        """
        if relative_to_robot and self.robot.pose:
            pose = self.robot.pose.define_pose_relative_this(pose)

        motion_prof = self._motion_profile_for_proto()
        # @TODO: the id_tag we supply can be used to cancel this action,
        #  however when we implement that we will need some way to get the id_tag
        #  out of this function.
        go_to_pose_request = protocol.GoToPoseRequest(x_mm=pose.position.x,
                                                      y_mm=pose.position.y,
                                                      rad=pose.rotation.angle_z.radians,
                                                      motion_prof=motion_prof,
                                                      id_tag=self._get_next_action_id(),
                                                      num_retries=num_retries)

        return await self.grpc_interface.GoToPose(go_to_pose_request)

    # TODO Check that num_retries is working (and if not, same for other num_retries).
    # TODO alignment_type coming out ugly in the docs without real values
    @connection.on_connection_thread()
    async def dock_with_cube(self,
                             target_object: objects.LightCube,
                             approach_angle: util.Angle = None,
                             alignment_type: protocol.AlignmentType = protocol.ALIGNMENT_TYPE_LIFT_PLATE,
                             distance_from_marker: util.Distance = None,
                             num_retries: int = 0) -> protocol.DockWithCubeResponse:
        """Tells Vector to dock with a light cube, optionally using a given approach angle and distance.

        While docking with the cube, Vector will use path planning.

        :param target_object: The LightCube object to dock with.
        :param approach_angle: Angle to approach the dock with.
        :param alignment_type: Which part of the robot to align with the object.
        :param distance_from_marker: How far from the object to approach (0 to dock)
        :param num_retries: Number of times to re-attempt action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.world.connect_cube()

                if robot.world.connected_light_cube:
                    dock_response = robot.behavior.dock_with_cube(robot.world.connected_light_cube)
                    docking_result = dock_response.result
        """
        if target_object is None:
            raise Exception("Must supply a target_object to dock_with_cube")

        motion_prof = self._motion_profile_for_proto()

        # @TODO: the id_tag we supply can be used to cancel this action,
        #  however when we implement that we will need some way to get the id_tag
        #  out of this function.
        dock_request = protocol.DockWithCubeRequest(object_id=target_object.object_id,
                                                    alignment_type=alignment_type,
                                                    motion_prof=motion_prof,
                                                    id_tag=self._get_next_action_id(),
                                                    num_retries=num_retries)
        if approach_angle is not None:
            dock_request.use_approach_angle = True
            dock_request.use_pre_dock_pose = True
            dock_request.approach_angle = approach_angle.radians
        if distance_from_marker is not None:
            dock_request.distance_from_marker = distance_from_marker.distance_mm

        return await self.grpc_interface.DockWithCube(dock_request)

    # Movement actions
    @connection.on_connection_thread()
    async def drive_straight(self,
                             distance: util.Distance,
                             speed: util.Speed,
                             should_play_anim: bool = True,
                             num_retries: int = 0) -> protocol.DriveStraightResponse:
        """Tells Vector to drive in a straight line.

        Vector will drive for the specified distance (forwards or backwards)

        Vector must be off of the charger for this movement action.

        :param distance: The distance to drive
            (>0 for forwards, <0 for backwards)
        :param speed: The speed to drive at
            (should always be >0, the abs(speed) is used internally)
        :param should_play_anim: Whether to play idle animations whilst driving
            (tilt head, hum, animated eyes, etc.)
        :param num_retries: Number of times to re-attempt action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector
            from anki_vector.util import degrees, distance_mm, speed_mmps

            with anki_vector.Robot() as robot:
                robot.behavior.drive_straight(distance_mm(200), speed_mmps(100))
        """

        # @TODO: the id_tag we supply can be used to cancel this action,
        #  however when we implement that we will need some way to get the id_tag
        #  out of this function.
        drive_straight_request = protocol.DriveStraightRequest(speed_mmps=speed.speed_mmps,
                                                               dist_mm=distance.distance_mm,
                                                               should_play_animation=should_play_anim,
                                                               id_tag=self._get_next_action_id(),
                                                               num_retries=num_retries)

        return await self.grpc_interface.DriveStraight(drive_straight_request)

    @connection.on_connection_thread()
    async def turn_in_place(self,
                            angle: util.Angle,
                            speed: util.Angle = util.Angle(0.0),
                            accel: util.Angle = util.Angle(0.0),
                            angle_tolerance: util.Angle = util.Angle(0.0),
                            is_absolute: bool = 0,
                            num_retries: int = 0) -> protocol.TurnInPlaceResponse:
        """Turn the robot around its current position.

        Vector must be off of the charger for this movement action.

        :param angle: The angle to turn. Positive
                values turn to the left, negative values to the right.
        :param speed: Angular turn speed (per second).
        :param accel: Acceleration of angular turn
                (per second squared).
        :param angle_tolerance: angular tolerance
                to consider the action complete (this is clamped to a minimum
                of 2 degrees internally).
        :param is_absolute: True to turn to a specific angle, False to
                turn relative to the current pose.
        :param num_retries: Number of times to re-attempt the turn in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector
            from anki_vector.util import degrees

            with anki_vector.Robot() as robot:
                robot.behavior.turn_in_place(degrees(90))
        """
        turn_in_place_request = protocol.TurnInPlaceRequest(angle_rad=angle.radians,
                                                            speed_rad_per_sec=speed.radians,
                                                            accel_rad_per_sec2=accel.radians,
                                                            tol_rad=angle_tolerance.radians,
                                                            is_absolute=is_absolute,
                                                            id_tag=self._get_next_action_id(),
                                                            num_retries=num_retries)

        return await self.grpc_interface.TurnInPlace(turn_in_place_request)

    # TODO Clamp angle to MIN_HEAD_ANGLE and MAX_HEAD_ANGLE.
    @connection.on_connection_thread()
    async def set_head_angle(self,
                             angle: util.Angle,
                             accel: float = 10.0,
                             max_speed: float = 10.0,
                             duration: float = 0.0,
                             num_retries: int = 0) -> protocol.SetHeadAngleResponse:
        """Tell Vector's head to move to a given angle.

        :param angle: Desired angle for Vector's head.
            (:const:`MIN_HEAD_ANGLE` to :const:`MAX_HEAD_ANGLE`).
        :param accel: Acceleration of Vector's head in radians per second squared.
        :param max_speed: Maximum speed of Vector's head in radians per second.
        :param duration: Time for Vector's head to move in seconds. A value
                of zero will make Vector try to do it as quickly as possible.
        :param num_retries: Number of times to re-attempt the action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector
            from anki_vector.util import degrees

            with anki_vector.Robot() as robot:
                robot.behavior.set_head_angle(degrees(-22.0))
                robot.behavior.set_head_angle(degrees(45.0))
        """
        set_head_angle_request = protocol.SetHeadAngleRequest(angle_rad=angle.radians,
                                                              max_speed_rad_per_sec=max_speed,
                                                              accel_rad_per_sec2=accel,
                                                              duration_sec=duration,
                                                              id_tag=self._get_next_action_id(),
                                                              num_retries=num_retries)

        return await self.grpc_interface.SetHeadAngle(set_head_angle_request)

    @connection.on_connection_thread()
    async def set_lift_height(self,
                              height: float,
                              accel: float = 10.0,
                              max_speed: float = 10.0,
                              duration: float = 0.0,
                              num_retries: int = 0) -> protocol.SetLiftHeightResponse:
        """Tell Vector's lift to move to a given height.

        :param height: desired height for Vector's lift 0.0 (bottom) to
                1.0 (top) (we clamp it to this range internally).
        :param accel: Acceleration of Vector's lift in radians per
                second squared.
        :param max_speed: Maximum speed of Vector's lift in radians per second.
        :param duration: Time for Vector's lift to move in seconds. A value
                of zero will make Vector try to do it as quickly as possible.
        :param num_retries: Number of times to re-attempt the action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.behavior.set_lift_height(1.0)
        """

        if height < 0.0:
            self.logger.warning("lift height %s too small, should be in 0..1 range - clamping", height)
            height = MIN_LIFT_HEIGHT_MM
        elif height > 1.0:
            self.logger.warning("lift height %s too large, should be in 0..1 range - clamping", height)
            height = MAX_LIFT_HEIGHT_MM
        else:
            height = MIN_LIFT_HEIGHT_MM + (height * (MAX_LIFT_HEIGHT_MM - MIN_LIFT_HEIGHT_MM))

        set_lift_height_request = protocol.SetLiftHeightRequest(height_mm=height,
                                                                max_speed_rad_per_sec=max_speed,
                                                                accel_rad_per_sec2=accel,
                                                                duration_sec=duration,
                                                                id_tag=self._get_next_action_id(),
                                                                num_retries=num_retries)

        return await self.grpc_interface.SetLiftHeight(set_lift_height_request)

    @connection.on_connection_thread(is_cancellable_behavior=True)
    async def turn_towards_face(self,
                                face: faces.Face,
                                num_retries: int = 0,
                                _behavior_id: int = None) -> protocol.TurnTowardsFaceResponse:
        """Tells Vector to turn towards this face.

        :param face_id: The face Vector will turn towards.
        :param num_retries: Number of times to reattempt the action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.behavior.turn_towards_face(1)

        Example of cancelling the :meth:`turn_towards_face` behavior:

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                turn_towards_face_future = robot.behavior.turn_towards_face(1)
                turn_towards_face_future.cancel()
        """
        turn_towards_face_request = protocol.TurnTowardsFaceRequest(face_id=face.face_id,
                                                                    max_turn_angle_rad=util.degrees(180).radians,
                                                                    id_tag=_behavior_id,
                                                                    num_retries=num_retries)

        return await self.grpc_interface.TurnTowardsFace(turn_towards_face_request)

    @connection.on_connection_thread(is_cancellable_behavior=True)
    async def go_to_object(self,
                           target_object: objects.LightCube,
                           distance_from_object,
                           num_retries: int = 0,
                           _behavior_id: int = None) -> protocol.GoToObjectResponse:
        """Tells Vector to drive to his Cube.

        :param target_object: The destination object. CustomObject instances are not supported.
        :param distance_from_object: The distance from the object to stop. This is the distance
                between the origins. For instance, the distance from the robot's origin
                (between Vector's two front wheels) to the cube's origin (at the center of the cube) is ~40mm.
        :param num_retries: Number of times to reattempt action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::
            import anki_vector
            from anki_vector.util import distance_mm

            with anki_vector.Robot() as robot:
                robot.world.connect_cube()

                if robot.world.connected_light_cube:
                    robot.behavior.go_to_object(robot.world.connected_light_cube, distance_mm(70.0))
        """
        if target_object is None:
            raise VectorException("Must supply a target_object of type LightCube to go_to_object")

        go_to_object_request = protocol.GoToObjectRequest(object_id=target_object.object_id,
                                                          distance_from_object_origin_mm=distance_from_object.distance_mm,
                                                          use_pre_dock_pose=False,
                                                          id_tag=_behavior_id,
                                                          num_retries=num_retries)

        return await self.grpc_interface.GoToObject(go_to_object_request)

    @connection.on_connection_thread(is_cancellable_behavior=True)
    async def roll_cube(self,
                        target_object: objects.LightCube,
                        approach_angle: util.Angle = None,
                        num_retries: int = 0,
                        _behavior_id: int = None) -> protocol.RollObjectResponse:
        """Tells Vector to roll a specified cube object.

        :param target_object: The cube to roll.
        :param approach_angle: The angle to approach the cube from. For example, 180 degrees will cause Vector to drive
                past the cube and approach it from behind.
        :param num_retries: Number of times to reattempt action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector
            from anki_vector.util import distance_mm

            with anki_vector.Robot() as robot:
                robot.world.connect_cube()

                if robot.world.connected_light_cube:
                    robot.behavior.roll_cube(robot.world.connected_light_cube)
        """
        if target_object is None:
            raise VectorException("Must supply a target_object of type LightCube to roll_cube")

        if approach_angle is None:
            use_approach_angle = False
            approach_angle = util.degrees(0)
        else:
            use_approach_angle = True
            approach_angle = approach_angle

        roll_object_request = protocol.RollObjectRequest(object_id=target_object.object_id,
                                                         approach_angle_rad=approach_angle.radians,
                                                         use_approach_angle=use_approach_angle,
                                                         use_pre_dock_pose=use_approach_angle,
                                                         id_tag=_behavior_id,
                                                         num_retries=num_retries)

        return await self.grpc_interface.RollObject(roll_object_request)

    @connection.on_connection_thread(is_cancellable_behavior=True)
    async def pop_a_wheelie(self,
                            target_object: objects.LightCube,
                            approach_angle: util.Angle = None,
                            num_retries: int = 0,
                            _behavior_id: int = None) -> protocol.PopAWheelieResponse:
        """Tells Vector to "pop a wheelie" using his light cube.

        :param target_object: The cube to push down on with Vector's lift, to start the wheelie.
        :param approach_angle: The angle to approach the cube from. For example, 180 degrees will cause Vector to drive
                past the cube and approach it from behind.
        :param num_retries: Number of times to reattempt action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector
            from anki_vector.util import distance_mm

            with anki_vector.Robot() as robot:
                robot.world.connect_cube()

                if robot.world.connected_light_cube:
                    robot.behavior.pop_a_wheelie(robot.world.connected_light_cube)
        """
        if target_object is None:
            raise VectorException("Must supply a target_object of type LightCube to pop_a_wheelie")

        if approach_angle is None:
            use_approach_angle = False
            approach_angle = util.degrees(0)
        else:
            use_approach_angle = True
            approach_angle = approach_angle

        pop_a_wheelie_request = protocol.PopAWheelieRequest(object_id=target_object.object_id,
                                                            approach_angle_rad=approach_angle.radians,
                                                            use_approach_angle=use_approach_angle,
                                                            use_pre_dock_pose=use_approach_angle,
                                                            id_tag=_behavior_id,
                                                            num_retries=num_retries)

        return await self.grpc_interface.PopAWheelie(pop_a_wheelie_request)

    @connection.on_connection_thread(is_cancellable_behavior=True)
    async def pickup_object(self,
                            target_object: objects.LightCube,
                            use_pre_dock_pose: bool = True,
                            num_retries: int = 0,
                            _behavior_id: int = None) -> protocol.PickupObjectResponse:
        """Instruct the robot to pick up his LightCube.

        While picking up the cube, Vector will use path planning.

        Note that actions that use the wheels cannot be performed at the same time,
        otherwise you may see a TRACKS_LOCKED error. Methods that use the wheels include
        :meth:`go_to_pose`, :meth:`dock_with_cube`, :meth:`turn_in_place`, :meth:`drive_straight`, and :meth:`pickup_object`.

        :param target_object: The LightCube object to dock with.
        :param use_pre_dock_pose: Whether or not to try to immediately pick
                up an object or first position the robot next to the object.
        :param num_retries: Number of times to reattempt action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.world.connect_cube()

                if robot.world.connected_light_cube:
                    robot.behavior.pickup_object(robot.world.connected_light_cube)
        """
        if target_object is None:
            raise VectorException("Must supply a target_object to dock_with_cube")

        pickup_object_request = protocol.PickupObjectRequest(object_id=target_object.object_id,
                                                             use_pre_dock_pose=use_pre_dock_pose,
                                                             id_tag=_behavior_id,
                                                             num_retries=num_retries)

        return await self.grpc_interface.PickupObject(pickup_object_request)

    @connection.on_connection_thread(is_cancellable_behavior=True)
    async def place_object_on_ground_here(self,
                                          num_retries: int = 0,
                                          _behavior_id: int = None) -> protocol.PlaceObjectOnGroundHereResponse:
        """Ask Vector to place the object he is carrying on the ground at the current location.

        :param num_retries: Number of times to reattempt action in case of a failure.

        Returns:
            A response from the robot with status information sent when this request successfully completes or fails.

        .. testcode::

            import anki_vector

            with anki_vector.Robot() as robot:
                robot.world.connect_cube()

                if robot.world.connected_light_cube:
                    robot.behavior.pickup_object(robot.world.connected_light_cube)
                    robot.behavior.place_object_on_ground_here()
        """
        place_object_on_ground_here_request = protocol.PlaceObjectOnGroundHereRequest(id_tag=_behavior_id,
                                                                                      num_retries=num_retries)

        return await self.grpc_interface.PlaceObjectOnGroundHere(place_object_on_ground_here_request)


class ReserveBehaviorControl():
    """A ReserveBehaviorControl object can be used to suppress the ordinary idle behaviors of
    the Robot and keep Vector still between SDK control instances.  Care must be taken when
    blocking background behaviors, as this may make Vector appear non-responsive.

    This class is most easily used via a built-in SDK script, and can be called on the command-line
    via the executable module :class:`anki_vector.reserve_control`:

        .. code-block:: bash

            python3 -m anki_vector.reserve_control

    As long as the script is running, background behaviors will not activate, keeping Vector
    still while other SDK scripts may take control.  Highest-level behaviors like returning to
    the charger due to low battery will still activate.

    System-specific shortcuts calling this executable module can be found in the examples/scripts
    folder.  These scripts can be double-clicked to easily reserve behavior control for the current
    SDK default robot.

    If there is a need to keep background behaviors from activating in a single script, the class
    may be used to reserve behavior control while in scope:

        .. code-block:: python

            import anki_vector
            from anki_vector import behavior

            with behavior.ReserveBehaviorControl():

                # At this point, Vector will remain still, even without
                # a Robot instance being in scope.

                # take control of the robot as usual
                with anki_vector.Robot() as robot:

                    robot.anim.play_animation("anim_turn_left_01")

                   # Robot will not perform idle behaviors until the script completes

    :param serial: Vector's serial number. The robot's serial number (ex. 00e20100) is located on
                   the underside of Vector, or accessible from Vector's debug screen. Used to
                   identify which Vector configuration to load.
    :param ip: Vector's IP address. (optional)
    :param config: A custom :class:`dict` to override values in Vector's configuration. (optional)
                   Example: :code:`{"cert": "/path/to/file.cert", "name": "Vector-XXXX", "guid": "<secret_key>"}`
                   where :code:`cert` is the certificate to identify Vector, :code:`name` is the
                   name on Vector's face when his backpack is double-clicked on the charger, and
                   :code:`guid` is the authorization token that identifies the SDK user.
                   Note: Never share your authentication credentials with anyone.
    :param behavior_activation_timeout: The time to wait for control of the robot before failing.
    """

    def __init__(self,
                 serial: str = None,
                 ip: str = None,
                 config: dict = None,
                 behavior_activation_timeout: int = 10):
        config = config if config is not None else {}
        self.logger = util.get_class_logger(__name__, self)
        config = {**util.read_configuration(serial, name=None, logger=self.logger), **config}
        self._name = config["name"]
        self._ip = ip if ip is not None else config["ip"]
        self._cert_file = config["cert"]
        self._guid = config["guid"]

        self._port = "443"
        if 'port' in config:
            self._port = config["port"]

        if self._name is None or self._ip is None or self._cert_file is None or self._guid is None:
            raise ValueError(
                "The Robot object requires a serial and for Vector to be logged in (using the app then running the anki_vector.configure executable submodule).\n"
                "You may also provide the values necessary for connection through the config parameter. ex: "
                '{"name":"Vector-XXXX", "ip":"XX.XX.XX.XX", "cert":"/path/to/cert_file", "guid":"<secret_key>"}')

        self._conn = connection.Connection(self._name, ':'.join([self._ip, self._port]), self._cert_file, self._guid,
                                           behavior_control_level=connection.CONTROL_PRIORITY_LEVEL.RESERVE_CONTROL)
        self._behavior_activation_timeout = behavior_activation_timeout

    def __enter__(self):
        self._conn.connect(self._behavior_activation_timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
