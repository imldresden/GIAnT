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


def convertTimestamp(timestamp):  # turns the Timestring into a Number of milliseconds
    global timestampOffset
    timestamp = str(timestamp).replace(".", "")
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
        return (x2, y2)
    result1 = (round(x1 + a * dx1, 5), round(y1 + a * dy1, 5))

    return result1


def get_index_from_time_percentage(percentage):
    import User
    return int(percentage * float(len(User.users[0].head_positions)))


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

    return (x, y, z)


def normalize_vector(vector):
    result = []
    length = get_length(vector)
    for i in range(0, len(vector)):
        result.append(float(vector[i]) / float(length))
    return result


def get_user_color_as_hex(index, opacity):
    import global_values
    import Options
    if index == -1:
        hls = [0, 0, 1]
    else:
        if index < 0 or index > 3:
            index = 0
            print "user color index out of range"
        hls = global_values.user_color_schemes[Options.COLOR_SCHEME][index]
    hls = colorsys.hsv_to_rgb(hls[0], min(1, hls[1] * pow(opacity, 4) * 4), hls[2])
    color = (int(hls[0] * 255), int(hls[1] * 255), int(hls[2] * 255))
    color = '%02x%02x%02x' % color
    return color
