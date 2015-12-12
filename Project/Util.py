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


"Ramer-Douglas-Peucker Algorithm"
NegInf = float('-inf')

def distance(v1, v2):
    """
        Calculate the distance between two points.
        
        PARAMETERS
        ==========
        v1, v2 >> The first and second vertices respectively.
        """
    dx = v2[0] - v1[0]
    dy = v2[1] - v1[1]
    return math.hypot(dx, dy)

def perpendicularDistance(point, line_start, line_end):
    """
        Calculate the perpendicular distance from a point to a line.
        
        PARAMETERS
        ==========
        point >> The point of which to calculate the distance from the line
        (must be an (x, y) tuple).
        
        line_start, line_end >> Start and end points defining the line respectively
        (must each be an (x, y) tuple).
        """
    x1, y1 = line_start
    x2, y2 = line_end
    vx, vy = point
    if x1 == x2:
        return abs(x1 - vx)
    m = (y2 - y1)/(x2 - x1)
    b = y1 - m*x1
    return abs(m * vx - vy + b)/math.sqrt(m*m + 1)

def _rdpApprox(points, tolerance, depth):
    """
        Internal Function: Recursively perform the RDP algorithm.
        """
    if not points:
        # In case the furthest point index discovered is equal to the length of the
        # list of points, leading to points[furthest:] sending in an empty list.
        return []
    elif len(points) <= 2:
        # BASE CASE:: No points to remove, only the start and the end points of the line.
        # Return it.
        return points
    elif len(points) == 3:
        # BASE CASE:: Our decomposition of the polygon has reached a minimum of 3 points.
        # Now all that is left is to remove the point in the middle (assuming it's distance
        # from the line is greater than the set tolerance).
        dist = perpendicularDistance(points[1],
                                      points[0],
                                      points[2]
                                      )
                                      if dist < tolerance:
                                          return [points[0], points[-1]]
                                      return points

max_dist = NegInf
    furthest = None
    
    start = 0
    start_point = points[start]
    
    if depth == 1:
        # In the initial approximation, we are given an entire polygon to approximate. This
        # means that the start and end points are the same, thus we cannot use the perpendicular
        # distance equation to calculate the distance a point is from the start since the start is
        # not a line. We have to use ordinary distance formula instead.
        get_distance = lambda point: distance(point, start_point)
    else:
        end_point = points[-1]
        get_distance = lambda point: perpendicularDistance(point, start_point, end_point)

# Find the farthest point from the norm.
for i, point in enumerate(points[1:], 1):
    dist = get_distance(point)
        if dist > max_dist:
            max_dist = dist
            furthest = i

# Recursively calculate the RDP approximation of the two polygonal chains formed by
# slicing at the index of the furthest discovered point.
prev_points = _rdpApprox(points[:furthest+1], tolerance, depth+1)
    next_points = _rdpApprox(points[furthest:], tolerance, depth+1)
    
    new_points = []
    for point in prev_points + next_points:
        # Filter out the duplicate points whilst maintaining order.
        # TODO:: There's probably some fancy slicing trick I just haven't figured out
        # that can be applied to prev_points and next_points so that we don't have to
        # do this, but it's not a huge bottleneck so we needn't worry about it now.
        if point not in new_points:
            new_points.append(point)

return new_points

def rdpPolygonApproximate(coordinates, tolerance):
    """
        Use the Ramer-Douglas-Peucker algorithm to approximate the points on a polygon.
        
        The RDP algorithm recursively cuts away parts of a polygon that stray from the
        average of the edges. It is a great algorithm for maintaining the overall form
        of the input polygon, however one should be careful when using this for larger
        polygons as the algorithm has an average complexity of T(n) = 2T(n/2) + O(n) and
        a worst case complexity of O(n^2).
        
        PARAMETERS
        ==========
        coordinates >> The coordinates of the polygon to approximate.
        
        tolerance >> The amount of tolerance the algorithm will use. The tolerance
        determines the minimum distance a point has to sway from the average
        before it gets deleted from the polygon. Thus, setting the tolerance to
        be higher should delete more points on the final polygon.
        
        That said, due to how the algorithm works there is a limit to the number
        of vertices that can be removed on a polygon. Setting the tolerance to
        float('inf') or sys.maxsize will not approximate the polygon to a single
        point. Usually the minimum points an approximated polygon can have if the
        original polygon had N points is between 2N/3 and N/3.
        
        FURTHER READING
        ===============
        For further reading on the Ramer-Douglas-Peucker algorithm, see
        http://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm
        """
    return _rdpApprox(coordinates, tolerance, 1)

if __name__ == '__main__':
    poly = [(3, 0), (4, 2), (5, 2), (5.5, 3), (5, 4), (4, 5), (5, 6),
            (7, 5), (7, 3), (8, 2.5), (8, 4), (9, 5), (8, 7), (7, 8), (6, 7),
            (4, 7.75), (3.5, 7.5), (3, 8), (3, 8.5), (2.5, 9), (1, 9), (0, 8),
            (2, 7), (1, 7), (0, 6), (1, 4), (2, 5), (2, 2), (3, 3), (2, 1)]
            print(rdpPolygonApproximate(poly, 3))
            print(rdpPolygonApproximate(poly, float('inf')))
