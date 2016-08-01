# -*- coding: utf-8 -*-

import colorsys
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


def get_user_color_as_hex(index, opacity):
    import global_values
    import options_panel
    if index == -1:
        hls = [0, 0, 1]
    else:
        if index < 0 or index > 3:
            index = 0
            print "user color index out of range"
        hls = global_values.user_color_schemes[options_panel.COLOR_SCHEME][index]
    hls = colorsys.hsv_to_rgb(hls[0], min(1, hls[1] * pow(opacity, 4) * 4), hls[2])
    color = (int(hls[0] * 255), int(hls[1] * 255), int(hls[2] * 255))
    color = '%02x%02x%02x' % color
    return color


def format_label_value(unit, value):
    """
    Format label values depending on units of measurement.
    :param unit: unit of measurement ('s', 'm')
    :param value: label value
    """

    # length units in centimeters
    if unit is "m":

        # cut zeros if value is integer
        if value % 1 in (0, 0.0):
            value = int(value)
        else:
            value = round(value, 4)

        return "{} m".format(value)

    # time units in seconds
    elif unit is "s":
        # calculate seconds and minutes from milliseconds
        ms = int((value - int(value)) * 1000+0.5)
        m, s = divmod(value, 60)
        label = "{:02d}:{:02d}".format(int(m), int(s))
        if ms != 0:
            label += ".{:03d}".format(ms)
        return label

    assert False
