#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

"""Control joysticks and gamepads from within PsychoPy.

For most backends, you do need a window using the same backend (and you need to 
be flipping it) for the joystick to be updated.

"""

__all__ = ['Joystick', 'getJoystickInterfaces']

from psychopy import logging, visual
from psychopy.hardware.base import BaseDevice
from psychopy.hardware.joystick._base import BaseJoystickInterface
from psychopy.hardware.joystick.backend_pyglet import JoystickInterfacePyglet

import numpy as np

backend = 'pyglet'  # 'pyglet' or 'pygame'


class Joystick(BaseDevice):
    """Class for interfacing with a multi-axis joystick or gamepad.

    Upon creating a `Joystick` object, the joystick device is opened and the 
    states of the device's axes and buttons can be read.

    Parameters
    ----------
    device : int or str
        The index or name of the joystick to control.

    Examples
    --------
    Typical usage::

        from psychopy.hardware import joystick
        from psychopy import visual

        joystick.backend='pyglet'  # must match the Window
        win = visual.Window([400,400], winType='pyglet')

        nJoys = joystick.getNumJoysticks()  # to check if we have any
        id = 0
        joy = joystick.Joystick(id)  # id must be <= nJoys - 1

        nAxes = joy.getNumAxes()  # for interest
        while True:  # while presenting stimuli
            joy.getX()
            # ...
            win.flip()  # flipping implicitly updates the joystick info

    Notes
    -----
    * You do need to be flipping frames (or dispatching events manually) in 
      order for the values of the joystick to be updated.
    * Currently under pyglet backends the axis values initialise to zero
      rather than reading the current true value. This gets fixed on the first 
      change to each axis.
    * Currently pygame (1.9.1) spits out lots of debug messages about the
      joystick and these can't be turned off :-/

    """
    def __init__(self, device=0, **kwargs):
        super(Joystick, self).__init__()
        # get the joystick device interface
        try:
            joyInterface = getJoystickInterfaces()[backend]
        except KeyError:
            logging.error(
                "No joystick interface found for backend '{}'".format(
                    backend))

        # create a device interface
        self._joy = joyInterface(device, **kwargs)

        # scale factors for the axes
        self._scaleX = self._scaleY = self._scaleZ = 1.0

    @staticmethod
    def getAvailableDevices():
        """Return a list of available joystick devices.

        This method is used by `DeviceManager` to get a list of available
        devices.

        Returns
        -------
        list
            A list of available joystick devices.

        """
        # use the selected backend class to get the available devices
        return getJoystickInterfaces()[backend].getAvailableDevices()

    def isSameDevice(self, otherDevice):
        """Check if the device is the same as another device.

        Parameters
        ----------
        otherDevice : Joystick
            The other device to compare against.

        Returns
        -------
        bool
            True if the devices are the same, False otherwise.

        """
        # only need to check the index since the device ID is unique
        return self._joy.isSameDevice(otherDevice._device)

    def open(self):
        """Open the joystick device.

        """
        self._joy.open()

    @property
    def isOpen(self):
        """Check if the joystick device is open.

        Returns
        -------
        bool
            True if the joystick device is open, False otherwise.

        """
        return self._joy.isOpen

    def close(self):
        """Close the joystick device.

        """
        self._joy.close()

    def __del__(self):
        """Close the joystick device when the object is deleted.

        """
        self.close()

    @property
    def name(self):
        """Name of the joystick reported by the system (`str`).
        """
        return self.getName()
    
    @property
    def deviceIndex(self):
        """The index of the joystick (`int`).
        """
        return self._deviceIndex

    @property
    def x(self):
        """The X axis value (`float`).
        """
        return self._joy.getX() * self._scaleX

    @property
    def y(self):
        """The Y axis value (`float`).
        """
        return self._joy.getY() * self._scaleY

    @property
    def z(self):
        """The Z axis value (`float`).
        """
        return self._joy.getZ() * self._scaleZ

    @property
    def scaleX(self):
        """Scale factor for the X axis (`float`).
        """
        return self._scaleX

    @scaleX.setter
    def scaleX(self, scale):
        if not isinstance(scale, (int, float)):
            raise TypeError("Scaling factor must be a numeric type.")
        self._scaleX = scale

    @property
    def scaleY(self):
        """Scale factor for the Y axis (`float`).
        """
        return self._scaleY

    @scaleY.setter
    def scaleY(self, scale):
        if not isinstance(scale, (int, float)):
            raise TypeError("Scaling factor must be a numeric type.")
        self._scaleY = scale

    @property
    def scaleZ(self):
        """Scale factor for the Z axis (`float`).
        """
        return self._scaleZ

    @scaleZ.setter
    def scaleZ(self, scale):
        if not isinstance(scale, (int, float)):
            raise TypeError("Scaling factor must be a numeric type.")
        self._scaleZ = scale

    def getName(self):
        """Return the manufacturer-defined name describing the device.
        """
        return self._joy.getName()

    def getNumButtons(self):
        """Return the number of digital buttons on the device.
        """
        return self._joy.getNumButtons()

    def getButton(self, buttonId):
        """Get the state of a given button.

        buttonId should be a value from 0 to the number of buttons-1
        """
        return self._joy.getButton(buttonId)

    def getAllButtons(self):
        """Get the state of all buttons as a list.
        """
        return self._joy.getAllButtons()

    def getAllHats(self):
        """Get the current values of all available hats as a list of tuples.

        Each value is a tuple (x, y) where x and y can be -1, 0, +1
        """
        return self._joy.getAllHats()

    def getNumHats(self):
        """Get the number of hats on this joystick.

        The GLFW backend makes no distinction between hats and buttons. Calling
        'getNumHats()' will return 0.

        """
        return self._joy.getNumHats()

    def getHat(self, hatId=0):
        """Get the position of a particular hat.

        The position returned is an (x, y) tuple where x and y
        can be -1, 0 or +1
        """
        return self._joy.getHat(hatId)

    def getX(self):
        """Return the X axis value (equivalent to joystick.getAxis(0))."""
        return self._joy.getX()

    def getY(self):
        """Return the Y axis value (equivalent to joystick.getAxis(1))."""
        return self._joy.getY()

    def getZ(self):
        """Return the Z axis value (equivalent to joystick.getAxis(2))."""
        return self._joy.getZ()

    def getAllAxes(self):
        """Get a list of all current axis values."""
        return self._joy.getAllAxes()

    def getNumAxes(self):
        """Return the number of joystick axes found.
        """
        return self._joy.getNumAxes()

    def getAxis(self, axisId):
        """Get the value of an axis by an integer id.

        (from 0 to number of axes - 1)
        """
        return self._joy.getAxis(axisId)


class XboxController(Joystick):
    """Joystick template class for the XBox 360 controller.

    Usage:

        xbctrl = XboxController(0)  # joystick ID
        y_btn_state = xbctrl.y  # get the state of the 'Y' button

    """
    def __init__(self, deviceIndex, **kwargs):
        deviceIndex = kwargs.get('id', deviceIndex)  # legacy param
        super(XboxController, self).__init__(deviceIndex)

        # validate if this is an Xbox controller by its reported name
        if self.name.find("Xbox 360") == -1:
            logging.warning("The connected controller does not appear "
                            "compatible with the 'XboxController' template. "
                            "Unexpected input behaviour may result!")

        if backend != 'glfw':
            logging.error("Controller templates are only supported when using "
                          "the GLFW window backend. You must also set "
                          "joystick.backend='glfw' prior to creating a "
                          "joystick.")


        # button mapping for the XBox controller
        self._button_mapping = {'a': 0,
                                'b': 1,
                                'x': 2,
                                'y': 3,
                                'left_shoulder': 4,
                                'right_shoulder': 5,
                                'back': 6,
                                'start': 7,
                                'left_stick': 8,
                                'right_stick': 9,
                                'up': 10,  # hat
                                'down': 11,
                                'left': 12,
                                'right': 13}

        # axes groups
        self._axes_mapping = {'left_thumbstick': (0, 1),
                              'right_thumbstick': (2, 3),
                              'triggers': (4, 5),
                              'dpad': (6, 7)}

    @property
    def a(self):
        return self.get_a()

    def get_a(self):
        """Get the 'A' button state.

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['a'])

    @property
    def b(self):
        return self.get_b()

    def get_b(self):
        """Get the 'B' button state.

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['b'])

    @property
    def x(self):
        return self.get_x()

    def get_x(self):
        """Get the 'X' button state.

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['x'])

    @property
    def y(self):
        return self.get_y()

    def get_y(self):
        """Get the 'Y' button state.

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['y'])

    @property
    def left_shoulder(self):
        return self.get_left_shoulder()

    def get_left_shoulder(self):
        """Get left 'shoulder' trigger state.

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['left_shoulder'])

    @property
    def right_shoulder(self):
        return self.get_right_shoulder()

    def get_right_shoulder(self):
        """Get right 'shoulder' trigger state.

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['right_shoulder'])

    @property
    def back(self):
        return self.get_back()

    def get_back(self):
        """Get 'back' button state (button to the right of the left joystick).

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['back'])

    @property
    def start(self):
        return self.get_start()

    def get_start(self):
        """Get 'start' button state (button to the left of the 'X' button).

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['start'])

    @property
    def hat_axis(self):
        return self.get_hat_axis()

    def get_hat_axis(self):
        """Get the states of the hat (sometimes called the 'directional pad').
        The hat can only indicate direction but not displacement.

        This function reports hat values in the same way as a joystick so it may
        be used interchangeably with existing analog joystick code.

        Returns a tuple (X,Y) indicating which direction the hat is pressed
        between -1.0 and +1.0. Positive values indicate presses in the right or
        up direction.

        :return: tuple, zero centered X, Y values.
        """
        # get button states
        button_states = self.getAllButtons()
        up = button_states[self._button_mapping['up']]
        dn = button_states[self._button_mapping['down']]
        lf = button_states[self._button_mapping['left']]
        rt = button_states[self._button_mapping['right']]

        # convert button states to 'analog' values
        return -1.0 * lf + rt, -1.0 * dn + up

    @property
    def left_thumbstick(self):
        return self.get_left_thumbstick()

    def get_left_thumbstick(self):
        """Get the state of the left joystick button; activated by pressing
        down on the stick.

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['left_stick'])

    @property
    def right_thumbstick(self):
        return self.get_right_thumbstick()

    def get_right_thumbstick(self):
        """Get the state of the right joystick button; activated by pressing
        down on the stick.

        :return: bool, True if pressed down
        """
        return self.getButton(self._button_mapping['right_stick'])

    def get_named_buttons(self, button_names):
        """Get the states of multiple buttons using names. A list of button
        states is returned for each string in list 'names'.

        :param button_names: tuple or list of button names
        :return:
        """

        button_states = []
        for button in button_names:
            button_states.append(self.getButton(self._button_mapping[button]))

        return button_states

    @property
    def left_thumbstick_axis(self):
        return self.get_left_thumbstick_axis()

    def get_left_thumbstick_axis(self):
        """Get the axis displacement values of the left thumbstick.

        Returns a tuple (X,Y) indicating thumbstick displacement between -1.0
        and +1.0. Positive values indicate the stick is displaced right or up.

        :return: tuple, zero centered X, Y values.
        """
        ax, ay = self._axes_mapping['left_thumbstick']

        # we sometimes get values slightly outside the range of -1.0 < x < 1.0,
        # so clip them to give the user what they expect
        ax_val = self._clip_range(self.getAxis(ax))
        ay_val = self._clip_range(self.getAxis(ay))

        return ax_val, ay_val

    @property
    def right_thumbstick_axis(self):
        return self.get_right_thumbstick_axis()

    def get_right_thumbstick_axis(self):
        """Get the axis displacement values of the right thumbstick.

        Returns a tuple (X,Y) indicating thumbstick displacement between -1.0
        and +1.0. Positive values indicate the stick is displaced right or up.

        :return: tuple, zero centered X, Y values.
        """
        ax, ay = self._axes_mapping['right_thumbstick']

        ax_val = self._clip_range(self.getAxis(ax))
        ay_val = self._clip_range(self.getAxis(ay))

        return ax_val, ay_val

    @property
    def trigger_axis(self):
        return self.get_trigger_axis()

    def get_trigger_axis(self):
        """Get the axis displacement values of both index triggers.

        Returns a tuple (L,R) indicating index trigger displacement between -1.0
        and +1.0. Values increase from -1.0 to 1.0 the further a trigger is
        pushed.

        :return: tuple, zero centered L, R values.
        """
        al, ar = self._axes_mapping['triggers']

        al_val = self._clip_range(self.getAxis(al))
        ar_val = self._clip_range(self.getAxis(ar))

        return al_val, ar_val

    def _clip_range(self, val):
        """Clip the range of a value between -1.0 and +1.0. Needed for joystick
        axes.

        :param val:
        :return:
        """
        if -1.0 > val:
            val = -1.0

        if val > 1.0:
            val = 1.0

        return val


def getJoystickInterfaces():
    """Return a list of joystick interfaces available.

    Returns
    -------
    list
        A list of joystick interfaces available.

    """
    foundJoystickInterfaces = {}

    # look for subclasses of JoystickInterface in this module's namespace
    for name in globals():
        obj = globals()[name]
        if isinstance(obj, type) and issubclass(obj, BaseJoystickInterface):
            if obj != BaseJoystickInterface:
                foundJoystickInterfaces[obj.backendName] = obj

    return foundJoystickInterfaces.copy()


def getAllJoysticks():
    """Enumerate all available joysticks and return a dictionary of their
    information.

    Returns
    -------
    dict
        A dictionary of all available joysticks with the joystick ID as the
        key and the keys containing information about the joystick. As a
        minimum, the dictionary will contain the key 'name' which contains the
        name of the joystick. The dictionary may contain additional information
        about the joystick if that information is available.

    """
    return Joystick.getAllJoysticks()


if __name__ == "__main__":
    pass
