from collections import OrderedDict
from random import Random
import OptionsPanel
import global_values, math, libavg, time_interval, variable_width_line

DISTANCE = 100  # maximum distance in cm between users
ANGLE = 90  # maximum viewing angle between users
MIN_DURATION = 50  # minimum time for continuous f-formation

X_1 = 0
X_2 = 1
Y_1 = 2
Y_2 = 3
USER_1 = 4
USER_2 = 5
INTENSITY = 6
NUMBER = 7
TIME = 8


class F_Formations(libavg.DivNode):
    def load_f_formations(self):
        import database
        self.all_f_formations = database.get_f_formations()
        self.all_f_formations_map = None
        self.all_f_formations_times = []
        for f_formation in self.all_f_formations:
            if self.all_f_formations_map == None:
                self.all_f_formations_map = {f_formation[NUMBER]: {f_formation[TIME]: f_formation}}
            else:
                if not f_formation[NUMBER] in self.all_f_formations_map:
                    self.all_f_formations_map[f_formation[NUMBER]] = {f_formation[TIME]: f_formation}
                else:
                    self.all_f_formations_map[f_formation[NUMBER]][f_formation[TIME]] = f_formation

        print "loading F-Formations done"

    def __init__(self, parent, **kwargs):
        super(F_Formations, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.load_f_formations()
        self.points = []
        self.opacities = []
        self.variable_width_lines = []
        self.calculate_dataset()
        # self.variable_width_lines.append(Variable_Width_Line.Variable_Width_Line(points=self.points, widths=None, opacities=self.opacities, userid=-1, parent=self, set_points_directly=True))

    def calculate_dataset(self):
        points_references = []
        for i in range(len(self.parent.main_visualization.canvas_objects)):
            points_references.append(self.parent.main_visualization.canvas_objects[i].points)

        points = []
        opacities = []

        times = []

        # takes the sampling directly from the main_visualization object of the parent(not very nice, I know)
        for point_reference in points_references[0]:
            part = point_reference[0] / self.parent.main_visualization.width
            times.append(round(time_interval.main_time_frame.get_time_for_part_in_interval(part) / global_values.time_step_size) * global_values.time_step_size)

        # takes the point positions directly from the main_visualization object
        for number in self.all_f_formations_map:
            current_points = []
            current_opacities = []
            current_dict = OrderedDict()
            for time in times:
                if self.all_f_formations_map[number].__contains__(time):
                    current_dict[time] = self.all_f_formations_map[number][time]
                    # {time: self.all_f_formations_map[number].get(time, []) for time in times}
            for k in current_dict.keys():
                if not current_dict[k]:
                    del current_dict[k]

            for time in current_dict:
                current_length = len(current_dict[time])
                if current_length == 0:
                    break
                point_index = int(time_interval.main_time_frame.get_part_in_interval_for_time(time) * len(points_references[0]))
                user_1 = current_dict[time][USER_1]
                user_2 = current_dict[time][USER_2]
                if point_index >= len(points_references[user_1]) or point_index >= len(points_references[user_2]):
                    break
                point = points_references[user_1][point_index]
                current_points.append(point)

                point2 = points_references[user_2][point_index]
                current_points.append(point2)

                current_opacities.append(max(0.1, min(1, 1 - 1 / current_dict[time][INTENSITY])))
                current_opacities.append(max(0.1, min(1, 1 - 1 / current_dict[time][INTENSITY])))

            if len(current_points) > 0:
                points.append(current_points)
                opacities.append(current_opacities)

        while len(self.variable_width_lines) > len(points):
            self.variable_width_lines[-1].node.unlink()
            self.variable_width_lines.pop()

        current_index = 0
        while len(self.variable_width_lines) < len(points):
            if len(points[current_index]) == 2:
                for i in range(2):
                    point = points[current_index][i]
                    points[current_index].append((point[0] + 10, point[1]))
                    opacities[current_index].append(opacities[current_index][i])

            self.variable_width_lines.insert(0,
                                             variable_width_line.VariableWidthLine(points=points[current_index], widths=None, opacities=opacities[current_index], userid=-1, parent=self,
                                                                                   set_points_directly=True))
            current_index += 1

        while current_index < len(self.variable_width_lines):
            self.variable_width_lines[current_index].set_values(points[current_index], None, opacities[current_index])
            current_index += 1

            # self.opacities = self.parent.main_visualization.canvas_objects[0].opacities
            # range_min = Time_Frame.main_time_frame.get_interval_range()[0]
            # range_max = Time_Frame.main_time_frame.get_interval_range()[1]
            # range_step = (range_max - range_min) / (self.width * global_values.samples_per_pixel)
            # selection = []
            # current_index = 0
            # previous_selected = None
            # last_number = 0
            # for sample_time in xrange(int(range_min), int(range_max), int(range_step)):
            #     while self.all_f_formations[current_index][TIME] < sample_time and current_index < len(self.all_f_formations) - 1:
            #         current_index += 1
            #     if current_index != 0:
            #         selected = self.all_f_formations[current_index]
            #         selection.append(selected)
            #         number = selected[NUMBER]
            #         if previous_selected == None:
            #             previous_selected = selected
            #
            #             # if len(self.points) <= number+1:
            #             # self.points.append([])
            #             # if len(self.points) == number:
            #             if last_number < number:
            #                 self.points.append((sample_time / (range_max - range_min) * self.width, previous_selected[X_2]*10))
            #                 self.points.append((sample_time / (range_max - range_min) * self.width, previous_selected[X_2]*10))
            #                 self.opacities.append(min(1, max(0, previous_selected[INTENSITY])))
            #                 self.opacities.append(min(1, max(0, selected[INTENSITY])))
            #                 last_number = number
            #                 self.points.append((sample_time / (range_max - range_min) * self.width, selected[X_1]*10))
            #                 self.points.append((sample_time / (range_max - range_min) * self.width, selected[X_1]*10))
            #                 self.opacities.append(min(1, max(0, selected[INTENSITY])))
            #                 self.opacities.append(min(1, max(0, selected[INTENSITY])))
            #         if previous_selected != selected:
            #             self.points.append((sample_time / (range_max - range_min) * self.width, selected[X_1]*10))
            #             self.points.append((sample_time / (range_max - range_min) * self.width, selected[X_2]*10))
            #             self.opacities.append(min(1, max(0, selected[INTENSITY])))
            #             self.opacities.append(min(1, max(0, selected[INTENSITY])))
            #             previous_selected = selected

    def update_time_frame(self, interval, draw_lines):
        if OptionsPanel.SHOW_F_FORMATIONS:
            self.calculate_dataset()
        else:
            for vvl in self.variable_width_lines:
                vvl.node.unlink()
                self.variable_width_lines.remove(vvl)


def check_for_f_formation(pos1, pos2, look_vector1, look_vector2):
    import util
    """
    Check if two positions, each with a looking direction, are in a F-Formation.
    :param pos1: Position in cm.
    :param pos2: Position in cm.
    :param look_vector1:
    :param look_vector2:
    :return: Strength of F-Formation.
    """

    v1 = util.normalize_vector(look_vector1)
    v2 = util.normalize_vector(look_vector2)
    distance = util.get_length((pos1[0] - pos2[0], pos1[1] - pos2[1]))
    if distance < DISTANCE:
        diff_vector = (pos2[0] - pos1[0], pos2[1] - pos1[1])
        angle1 = angle(v1, diff_vector)
        angle2 = angle(v2, (-diff_vector[0], -diff_vector[1]))
        if abs(angle1) > math.pi / 2 or abs(angle2) > math.pi / 2 or abs(angle1 - angle2) > ANGLE:
            return 0

        angle_similarity = 1 / (0.2 + abs(angle1 - angle2))
        print "similarity : " + str(angle_similarity)

        return 20 / util.get_length((pos1[0] + 100 * v1[0] - pos2[0] + 100 * v2[0], pos1[1] + 100 * v1[1] - pos2[1] + 100 * v2[1])) * angle_similarity

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
