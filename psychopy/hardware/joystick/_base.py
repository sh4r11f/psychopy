#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

"""Base classes for joystick and gamepad interfaces.
"""


class BaseJoystickInterface:
    """Class for defining an interface for joystick and gamepad devices.

    This class is used as a template for creating joystick and gamepad devices
    that can be used with PsychoPy. It provides a common interface for
    interacting with joystick and gamepad devices. This class should not be
    instantiated directly, but should be subclassed to create a specific
    joystick or gamepad device interface.

    """
    backendName = None
    def __init__(self, device=0, **kwargs):
        self._device = None

    def isSameDevice(self, otherDevice):
        """Check if the device is the same as another device.

        Parameters
        ----------
        otherDevice : BaseJoystickDevice
            The other device to compare against.

        Returns
        -------
        bool
            True if the devices are the same, False otherwise.

        """
        return self.deviceIndex == otherDevice.deviceIndex
    
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
        raise NotImplementedError
    
    def open(self):
        """Open the joystick device.

        """
        raise NotImplementedError
    
    @property
    def isOpen(self):
        """Check if the joystick device is open.

        Returns
        -------
        bool
            True if the joystick device is open, False otherwise.

        """
        raise NotImplementedError

    def close(self):
        """Close the joystick device.

        """
        raise NotImplementedError

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

    def getName(self):
        """Return the manufacturer-defined name describing the device.
        """
        raise NotImplementedError

    def getNumButtons(self):
        """Return the number of digital buttons on the device.
        """
        raise NotImplementedError

    def getButton(self, buttonId):
        """Get the state of a given button.

        buttonId should be a value from 0 to the number of buttons-1
        """
        raise NotImplementedError

    def getAllButtons(self):
        """Get the state of all buttons as a list.
        """
        raise NotImplementedError

    def getAllHats(self):
        """Get the current values of all available hats as a list of tuples.

        Each value is a tuple (x, y) where x and y can be -1, 0, +1
        """
        raise NotImplementedError

    def getNumHats(self):
        """Get the number of hats on this joystick.

        """
        raise NotImplementedError

    def getHat(self, hatId=0):
        """Get the position of a particular hat.

        The position returned is an (x, y) tuple where x and y
        can be -1, 0 or +1
        """
        raise NotImplementedError

    def getX(self):
        """Return the X axis value (equivalent to joystick.getAxis(0))."""
        raise NotImplementedError

    def getY(self):
        """Return the Y axis value (equivalent to joystick.getAxis(1))."""
        raise NotImplementedError

    def getZ(self):
        """Return the Z axis value (equivalent to joystick.getAxis(2))."""
        raise NotImplementedError

    def getAllAxes(self):
        """Get a list of all current axis values."""
        raise NotImplementedError

    def getNumAxes(self):
        """Return the number of joystick axes found.

        """
        raise NotImplementedError

    def getAxis(self, axisId):
        """Get the value of an axis by an integer id.

        (from 0 to number of axes - 1)
        """
        raise NotImplementedError
