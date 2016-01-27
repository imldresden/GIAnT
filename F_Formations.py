__author__ = 'KillytheBid'
import Util
import math


def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))


def length(v):
    return math.sqrt(dotproduct(v, v))


def angle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))


# pos1, pos2 in cm
# vectors normalized
def check_for_f_formation(pos1, pos2, look_vector1, look_vector2, threshold=200):
    print
    Util.normalize_vector
    v1 = Util.normalize_vector(look_vector1)
    v2 = Util.normalize_vector(look_vector2)
    distance = Util.get_length((pos1[0] - pos2[0], pos1[1] - pos2[1]))
    if distance < threshold:
        diff_vector = (pos2[0] - pos1[0], pos2[1] - pos1[1])
        angle1 = angle(v1, diff_vector)
        angle2 = angle(v2, (-diff_vector[0], -diff_vector[1]))
        if abs(angle1) > math.pi / 2 or abs(angle2) > math.pi / 2 or abs(angle1 - angle2) > 80:
            return None

        angle_similarity = 1 / (0.2 + abs(angle1 - angle2))
        average_angle = abs((angle1 + angle2) / 2)
        print "similarity : " + str(angle_similarity)
        print "average    : " + str(average_angle)

        return 20 / Util.get_length((pos1[0] + 100 * v1[0] - pos2[0] + 100 * v2[0], pos1[1] + 100 * v1[1] - pos2[1] + 100 * v2[1])) * angle_similarity

    else:
        return None

