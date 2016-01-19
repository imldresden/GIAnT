import math
import sys
import global_values
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

    # fixes the weird spike artifacts (not a pretty solution though)
    if a < -3 or a > 3:
        return (x2, y2)
    result1 = (round(x1 + a * dx1, 5), round(y1 + a * dy1, 5))

    return result1


def r_pretty(dmin, dmax, n, time=False):
    """
    calculates "nice" ticks for axis
    """

    min_n = int(n / 3)                          # non-negative integer giving minimal number of intervals n
    shrink_small = 0.75                         # positive numeric by which a default scale is shrunk
    high_unit_bias = 1.5                        # non-negative numeric, typically > 1
                                                # the interval unit is determined as {1,2,5,10} * b, a power of 10
                                                # larger high_unit_bias favors larger units
    unit5_bias = 0.5 + 1.5 * high_unit_bias     # non-negative numeric multiplier favoring factor 5 over 2

    h = high_unit_bias
    h5 = unit5_bias
    ndiv = n

    dx = dmax - dmin

    if dx is 0 and dmax is 0:
        cell = 1.0
        i_small = True
        u = 1
    else:
        cell = max(abs(dmin), abs(dmax))
        if h5 >= 1.5 * h + 0.5:
            u = 1 + (1.0 / (1 + h))
        else:
            u = 1 + (1.5 / (1 + h5))
        i_small = dx < (cell * u * max(1.0, ndiv) * 1e-07 * 3.0)

    if i_small:
        if cell > 10:
            cell = 9 + cell / 10
            cell = cell * shrink_small
        if min_n > 1:
            cell = cell / min_n
    else:
        cell = dx
        if ndiv > 1:
            cell = cell / ndiv
    if cell < 20 * 1e-07:
        cell = 20 * 1e-07

    base = 10.00**math.floor(math.log10(cell))
    unit = base

    # time values have different preferred values
    if time:
        if (2 * base) - cell < h * (cell - unit):
            unit = 2.0 * base
            if (3 * base) - cell < h * (cell - unit):
                unit = 3.0 * base
                if (6 * base) - cell < h5 * (cell - unit):
                    unit = 6.0 * base
                    if (10 * base) - cell < h * (cell - unit):
                        unit = 10.0 * base
    else:
        if (2 * base) - cell < h * (cell - unit):
            unit = 2.0 * base
            if (5 * base) - cell < h5 * (cell - unit):
                unit = 5.0 * base
                if (10 * base) - cell < h * (cell - unit):
                    unit = 10.0 * base

    ns = math.floor(dmin / unit + 1e-07)
    nu = math.ceil(dmax / unit - 1e-07)

    # extend range out beyond the data
    while ns * unit > dmin + (1e-07 * unit):
        ns -= 1
    while nu * unit < dmax - (1e-07 * unit):
        nu += 1

    # if not enough labels, extend range out to make more (labels beyond data!)
    k = math.floor(0.5 + nu-ns)
    if k < min_n:
        k = min_n - k
        if ns >= 0:
            nu = nu + k / 2
            ns = ns - k / 2 + k % 2
        else:
            ns = ns - k / 2
            nu = nu + k / 2 + k % 2
        ndiv = min_n
    else:
        ndiv = k

    graphmin = ns * unit
    graphmax = nu * unit
    count = int(math.ceil(graphmax - graphmin) / unit)
    res = [graphmin + k * unit for k in range(count + 1)]
    if res[0] < dmin:
        res[0] = dmin
    if res[-1] > dmax:
        res[-1] = dmax
    return res


def getColorAsHex(index, opacity):
    if index < 0 or index > 3:
        index = 0
        print "color index out of range"
    hsv = global_values.colors_hsv[index]
    hsv = colorsys.hsv_to_rgb(hsv[0], min(1, hsv[1] * opacity * opacity * opacity * opacity * 4), hsv[2])
    color = (int(hsv[0] * 255), int(hsv[1] * 255), int(hsv[2] * 255))
    color = '%02x%02x%02x' % color
    return color
