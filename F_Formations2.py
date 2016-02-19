import global_values, math, libavg, Time_Frame, Variable_Width_Line

DISTANCE = 100  # maximum distance in cm between users
ANGLE = 90  # maximum viewing angle between users

X_1 = 0
X_2 = 1
Y_1 = 2
Y_2 = 3
USER_1 = 4
USER_2 = 5
INTENSITY = 6
TIME = 7


class F_Formations(libavg.DivNode):
    all_f_formations = []

    def load_f_formations(self):
        import database
        global all_f_formations
        self.all_f_formations = database.get_f_formations()

    def __init__(self, **kwargs):
        super(F_Formations, self).__init__(**kwargs)
        self.registerInstance(self, self.parent)
        self.load_f_formations()
        self.points = []
        self.opacities = []

        self.variable_width_line = Variable_Width_Line.Variable_Width_Line(points=self.points, widths=None, opacities=self.opacities, userid=-1, parent=self, set_points_directly=True)

    def calculate_dataset(self):

        range_min = Time_Frame.main_time_frame.get_interval_range()[0]
        range_max = Time_Frame.main_time_frame.get_interval_range()[1]
        range_step = (range_max - range_min) / (self.width * global_values.samples_per_pixel)
        selection = []
        current_index = 0
        for sample_time in xrange(range_min, range_max, range_step):
            while self.all_f_formations[current_index][TIME] < sample_time:
                current_index += 1
            if current_index != 0:
                selected = self.all_f_formations[sample_time]
                selection.append(selected)
                self.points.append((selected[X_1], selected[Y_1]))
                self.points.append((selected[X_2], selected[Y_2]))
                self.opacities.append(min(1, max(0, selected[INTENSITY])))

    def update_time_frame(self, interval, draw_lines):
        self.calculate_dataset()
        self.variable_width_line.set_values(self.points, None, self.opacities)


def check_for_f_formation(pos1, pos2, look_vector1, look_vector2):
    import Util
    """
    Check if two positions, each with a looking direction, are in a F-Formation.
    :param pos1: Position in cm.
    :param pos2: Position in cm.
    :param look_vector1:
    :param look_vector2:
    :return: Strength of F-Formation.
    """

    v1 = Util.normalize_vector(look_vector1)
    v2 = Util.normalize_vector(look_vector2)
    distance = Util.get_length((pos1[0] - pos2[0], pos1[1] - pos2[1]))
    if distance < DISTANCE:
        diff_vector = (pos2[0] - pos1[0], pos2[1] - pos1[1])
        angle1 = angle(v1, diff_vector)
        angle2 = angle(v2, (-diff_vector[0], -diff_vector[1]))
        if abs(angle1) > math.pi / 2 or abs(angle2) > math.pi / 2 or abs(angle1 - angle2) > ANGLE:
            return 0

        angle_similarity = 1 / (0.2 + abs(angle1 - angle2))
        average_angle = abs((angle1 + angle2) / 2)
        print "similarity : " + str(angle_similarity)
        print "average    : " + str(average_angle)

        return 20 / Util.get_length((pos1[0] + 100 * v1[0] - pos2[0] + 100 * v2[0], pos1[1] + 100 * v1[1] - pos2[1] + 100 * v2[1])) * angle_similarity

    else:
        return 0


def point_distance(p1, p2):
    """
    Distance between two 2D-Points.
    :param p1: Point 1
    :param p2: Point 2
    :return: Distance
    """
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def length(v):
    """
    Length of a Vector
    :param v: Vector
    :return: Length
    """
    return math.sqrt(dot_product(v, v))


def normalize(v):
    """
    Normalize vector.
    :param v: Vector
    :return: Normalized Vector
    """
    if length(v) == 0:
        return 0, 0
    else:
        return v[0] / length(v), v[1] / length(v)


def angle(v1, v2):
    """
    Angle between two vectors
    :param v1: Vector 1
    :param v2: Vector 2
    :return: Angle in radians
    """
    if length(v1) == 0 or length(v2) == 0:
        return 0
    else:
        return math.acos(dot_product(v1, v2) / (length(v1) * length(v2)))


def dot_product(v1, v2):
    """
    Dot product.
    :param v1: Vector 1
    :param v2: Vector 2
    :return:
    """
    return sum((a * b) for a, b in zip(v1, v2))
