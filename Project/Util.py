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


def getDistance(vec):
    value = 0
    for component in vec:
        value += component*component

    return math.sqrt(value)


def cleanString(string):
    patterns = ("\\", "\'", "[", " ", "]")
    result = string
    for pattern in patterns:
        result = result.replace(pattern, "")
    return result


def convertTimestamp(timestamp): # turns the Timestring into a Number of milliseconds
    global timestampOffset
    timestamp = str(timestamp).replace(".", "")
    split = timestamp.split(":")
    result = int(split[2]) + int(split[1])*60*1000 + int(split[0])*60*60*1000
    if result < timestampOffset:
        timestampOffset = result
    return result


def shiftTimestamp(timestamp):
    return timestamp-timestampOffset
