import math
import sys

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
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])  # Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        #raise Exception('lines do not intersect')
        return line1[0]

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

#calculate_line_intersection((0,0),(0,1),(1,1),0.1, 0.3, 0.1)