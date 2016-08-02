# -*- coding: utf-8 -*-

import math

def get_look_direction(pitch, yaw):
    x = 0
    y = 0
    z = 1

    # pitch
    pitch_cos = math.cos(pitch)
    pitch_sin = math.sin(pitch)

    new_z = z * pitch_cos
    new_y = z * pitch_sin
    z = new_z
    y = new_y

    yaw_cos = math.cos(yaw)
    yaw_sin = math.sin(yaw)
    # yaw
    new_x = - z * yaw_sin
    new_z = x * yaw_sin + z * yaw_cos
    x = new_x
    z = new_z

    return -x, y, z


def format_label_value(unit, value):
    if unit is "m":  # meters
        # cut zeros if value is integer
        if value % 1 in (0, 0.0):
            value = int(value)
        else:
            value = round(value, 4)

        return "{} m".format(value)

    elif unit is "s": # seconds
        ms = int((value - int(value)) * 1000+0.5)
        m, s = divmod(value, 60)
        label = "{:02d}:{:02d}".format(int(m), int(s))
        if ms != 0:
            label += ".{:03d}".format(ms)
        return label

    assert False
