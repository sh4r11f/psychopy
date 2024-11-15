#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019-2024 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

"""Mappings for common joystick and gamepad devices.
"""

__all__ = ['getAvailableInputSchemes', 'getInputScheme']

import sys
import os
import json

inputMapping = {}  # mappings are stored here

# Default joystick mapping
inputMapping['default'] = {
    'name': 'Default',
    'axes': {
        'X': 0,
        'Y': 1,
        'Z': 2,
        'XY': (0, 1),
        'RX': 3,
        'RY': 4,
        'RZ': 5
    },
    'buttons': {
        'A': 0,
        'B': 1,
        'X': 2,
        'Y': 3
    },
    'hats': {}
}

# Xbox 360 controller
inputMapping['xbox'] = {
    'name': 'Xbox 360',
    'axes': {
        'leftX': 0,
        'leftY': 1,
        'left': (0, 1),
        'thumbL': (0, 1),  # same as left, just more explicit
        'rightX': 2,
        'rightY': 3,
        'right': (2, 3),
        'thumbR': (2, 3),
        'triggerL': 4,
        'triggerR': 5,
        'triggers': (4, 5)
    },
    'buttons': {
        'A': 0,
        'B': 1,
        'X': 2,
        'Y': 3,
        'shoulderL': 4,
        'shoulderR': 5,
        'back': 6,
        'start': 7,
        'stickL': 8,
        'stickR': 9,
        'up': 10,  # hat
        'down': 11,
        'left': 12,
        'right': 13
    },
    'hats': {}
}

# PS3 controller
inputMapping['ps3'] = {
    'name': 'PS3 Dual-Shock',
    'axes': {
        'leftX': 0,
        'leftY': 1,
        'left': (0, 1),
        'thumbL': (0, 1),  # same as left, just more explicit
        'rightX': 2,
        'rightY': 3,
        'right': (2, 3),
        'thumbR': (2, 3),
        'triggerL': 4,
        'triggerR': 5,
        'triggers': (4, 5)
    },
    'buttons': {
        'cross': 0,
        'circle': 1,
        'square': 2,
        'triangle': 3,
        'shoulderL': 4,
        'shoulderR': 5,
        'select': 6,
        'start': 7,
        'stickL': 8,
        'stickR': 9,
        'up': 10,  # hat
        'down': 11,
        'left': 12,
        'right': 13
    },
    'hats': {}
}

# Logitech F310 controller
inputMapping['f310'] = {
    'name': 'Logitech F310',
    'axes': {
        'leftX': 0,
        'leftY': 1,
        'left': (0, 1),
        'thumbL': (0, 1),  # same as left, just more explicit
        'rightX': 2,
        'rightY': 3,
        'right': (2, 3),
        'thumbR': (2, 3),
        'triggerL': 4,
        'triggerR': 5,
        'triggers': (4, 5)
    },
    'buttons': {
        'A': 0,
        'B': 1,
        'X': 2,
        'Y': 3,
        'shoulderL': 4,
        'shoulderR': 5,
        'back': 6,
        'start': 7,
        'stickL': 8,
        'stickR': 9,
        'up': 10,  # hat
        'down': 11,
        'left': 12,
        'right': 13
    },
    'hats': {}
}

# same as f310, but with different name
inputMapping['f710'] = {
    'name': 'Logitech F710 Controller',
    'axes': inputMapping['f310']['axes'],
    'buttons': inputMapping['f310']['buttons'],
    'hats': inputMapping['f310']['hats']
}

# Thrustmaster T-Flight Hotas X
# Aliases for buttons as they appear on the device are provided
inputMapping['hotasx'] = {
    'name': 'Thrustmaster T-Flight Hotas X',
    'axes': {
        'X': 0,
        'Y': 1,
        'Z': 2, 'rudderL': 2, 'slider': 2,
        'XY': (0, 1), 'stick': (0, 1),
        'RX': 3, 'throttle': 3,
        'RY': 4,
        'RZ': 5, 'rudderR': 5
    },
    'buttons': {
        'button1': 0, 'trigger': 0,
        'button2': 1, 'L1': 1,
        'button3': 2, 'R3': 2,           
        'button4': 3, 'L3': 3,
        'button5': 4, 'square': 4,
        'button6': 5, 'X': 5,
        'button7': 6, 'circle': 6,
        'button8': 7, 'triangle': 7,
        'button9': 8, 'R2': 8,
        'button10': 9, 'L2': 9,
        'button11': 10, 'select': 10,
        'button12': 11, 'start': 11
    },
    'hats': {
        'hat': 0  # joystick hat
    }
}

# Oculus Rift and Quest Touch controllers
inputMapping['ovrtouch'] = {
    'name': 'Oculus Touch',
    'axes': {
        'thumbLX': 0,
        'thumbLY': 1,
        'thumbL': (0, 1),
        'thumbRX': 2,
        'thumbRY': 3,
        'thumbR': (2, 3),
        'triggerL': 4,
        'triggerR': 5,
        'triggers': (4, 5)
    },
    'buttons': {
        'A': 0,
        'B': 1,
        'X': 2,
        'Y': 3,
        'shoulderL': 4,
        'shoulderR': 5,
        'thumbL': 6,
        'thumbR': 7,
        'up': 8,  # hat
        'down': 9,
        'left': 10,
        'right': 11
    },
    'hats': {}
}


def getAvailableInputSchemes():
    """Get a list of available input schemes.

    Returns
    -------
    list
        A list of available input schemes.

    """
    return list(inputMapping.keys())


def getInputScheme(name):
    """Get an input scheme by name.

    Parameters
    ----------
    name : str
        The name of the input scheme to get.

    Returns
    -------
    dict or None
        The input scheme. None if the input scheme does not exist.

    """
    return inputMapping.get(name, None)


if __name__ == "__main__":
    print(getAvailableInputSchemes())
    print(getInputScheme('hotasx'))