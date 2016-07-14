# -*- coding: utf-8 -*-

import math
import sys
import colorsys

timestampOffset = sys.maxint


def addVectors(vec1, vec2):
    if len(vec1) != len(vec2):
        print("Util.addVectors: the two vectors " + vec1 + " and " + vec2 + " aren't the same size, vec1 is returned.")
        return vec1
    newTuple = ()
    for index in range(0, len(vec1)):
        newTuple += (vec1[index] + vec2[index]),
    return newTuple


def get_length(vector):
    value = 0
    for component in vector:
        value += component * component

    return math.sqrt(value)


def cleanString(string):
    patterns = ("\\", "\'", "[", " ", "]")
    result = string
    for pattern in patterns:
        result = result.replace(pattern, "")
    return result


def convertTimestamp(timestamp):
    """
    Turns the Timestring into a Number of milliseconds.
    :param timestamp:
    :return:
    """
    global timestampOffset
    split = timestamp.split(":")
    split[2] = float(str(split[2])) * 1000  # converting into whole milliseconds
    hours = int(split[0]) * 60 * 60 * 1000
    minutes = int(split[1]) * 60 * 1000
    milliseconds = int(split[2])
    result = hours + minutes + milliseconds
    if result < timestampOffset:
        timestampOffset = result
    return result


def line_intersection(line1, line2):
    x1 = line1[0][0]
    dx1 = line1[1][0] - x1
    x2 = line2[0][0]
    dx2 = line2[1][0] - x2

    y1 = line1[0][1]
    dy1 = line1[1][1] - y1
    y2 = line2[0][1]
    dy2 = line2[1][1] - y2

    try:
        a = (dy2 * (x1 - x2) + dx2 * (y2 - y1)) / (dx2 * dy1 - dx1 * dy2)
    except ZeroDivisionError:
        return (x2, y2)

    threshold = 2
    # fixes the weird spike artifacts (not a pretty solution though)
    if a < -threshold or a > threshold:
        return x2, y2
    result1 = (round(x1 + a * dx1, 5), round(y1 + a * dy1, 5))

    return result1


def get_index_from_time_percentage(percentage):
    import User
    return int(percentage * float(len(User.users[0].head_positions_integral)))


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


def normalize_vector(vector):
    result = []
    length = get_length(vector)
    for i in range(0, len(vector)):
        result.append(float(vector[i]) / float(length))
    return result


def get_user_color_as_hex(index, opacity):
    import global_values
    import OptionsPanel
    if index == -1:
        hls = [0, 0, 1]
    else:
        if index < 0 or index > 3:
            index = 0
            print "user color index out of range"
        hls = global_values.user_color_schemes[OptionsPanel.COLOR_SCHEME][index]
    hls = colorsys.hsv_to_rgb(hls[0], min(1, hls[1] * pow(opacity, 4) * 4), hls[2])
    color = (int(hls[0] * 255), int(hls[1] * 255), int(hls[2] * 255))
    color = '%02x%02x%02x' % color
    return color


def format_label_value(unit, value, short=False):
    """
    Format label values depending on units of measurement.
    :param unit: unit of measurement ('ms', 'cm')
    :param value: label value in ms
    :param short: short representation (no ms above 1 second) if True
    :return: String with formatted label value
    """
    def __format_ms(ms):
        """
        Add leading zero(s) to milliseconds if necessary
        :param ms: milliseconds
        :return: String with three digit ms
        """
        str_ms = ms
        if ms < 100:
            str_ms = "0{}".format(ms)
            if ms < 10:
                str_ms = "0{}".format(str_ms)
        return str_ms

    str_v = value

    # length units in centimeters
    if unit is "cm":

        meter = value / 100

        # cut zeros if value is integer
        if meter % 1 in (0, 0.0):
            meter = int(meter)
        else:
            meter = round(meter, 4)

        str_v = "{} m".format(meter)

    # time units in milliseconds
    elif unit is "ms":
        # calculate seconds and minutes from milliseconds
        s, ms = divmod(value, 1000)
        m, s = divmod(s, 60)

        ms = int(ms)
        s = int(s)
        m = int(m)

        str_ms = ""
        str_s = ""
        str_m = ""

        if ms is 0 and s is 0 and m is 0:
            str_m = "0 min"
        if m > 0:
            str_m = "{} min ".format(m)

        if ms > 0:
            if short and m <= 0 and s <= 0:
                str_ms = "{} ms".format(__format_ms(ms))
            if not short:
                str_ms = "{} ms".format(__format_ms(ms))

        if s > 0:
            if ms > 0:
                if short:
                    str_s = "{} s".format(s)
                else:
                    str_s = "{},".format(s)
                    str_ms = "{} s".format(__format_ms(ms))
            else:
                str_s = "{} s ".format(s)
        else:
            if m > 0 and ms > 0:
                if short:
                    str_s = "{} s".format(s)
                else:
                    str_s = "{},".format(s)
                    str_ms = "{} s".format(__format_ms(ms))

        str_v = "{}{}{}".format(str_m, str_s, str_ms)

    # no specific units defined
    else:
        # cut zeros if value is integer
        if value % 1 in (0, 0.0):
            value = int(value)
        # add SI prefix for one million
        if value >= 1000000:
            str_v = "{} M".format(value / 1000000)
        # add SI prefix for one thousand
        elif value >= 1000:
            str_v = "{} k".format(value / 1000)

    return str_v


def change_smoothness(value):
    """
    Changes global_values.averaging_count.
    :param value: value to change smoothness to
    """
    import global_values
    if value <= 0:
        value = global_values.min_averaging_count
    elif value > global_values.max_averaging_count:
        value = global_values.max_averaging_count
    global_values.averaging_count = int(value)
    global_values.samples_per_pixel = max(0.1, min(0.3, 50 / value))

    # publish changes
    from Time_Frame import main_time_frame
    main_time_frame.publish(draw_lines=True)

