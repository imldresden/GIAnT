from libavg import app, avg
import libavg
import User
import Util
import axis
import Visualization
import global_values
import math


class main_drawer(app.MainDiv):
    last_time = 0
    visualizations = []
    resolution = (1920, 1000)
    viewport_change_duration = 0.3
    '''
    zoom_target = 1
    zoom_current = 1
    zoom_last = 1
    zoom_amount = 0.1
    zoom_change_progress = 0
    zoom_change_starttime = 0

    shift_target = 0.5
    shift_current = 0.5
    shift_last = 0.5
    shift_change_progress = 0
    shift_change_starttime = 0
    '''

    def onInit(self):
        # self.resolution = libavg.app.instance._resolution
        self.resolution = (libavg.app.instance._resolution[0], libavg.app.instance._resolution[1] - 80)
        libavg.RectNode(pos=(0, 0), size=self.resolution, fillcolor='ffffff', parent=self, strokewidth=0)
        for userid in range(1, 5):
            user = User.User(userid)
        self.visualizations.append(Visualization.Visualization(parent=self, size=self.resolution, position=(0, 0)))
        self.subscribe(avg.Node.MOUSE_WHEEL, self.onMouseWheel)
        app.keyboardmanager.bindKeyDown(keyname='Right', handler=self.shift_forward)
        app.keyboardmanager.bindKeyDown(keyname='Left', handler=self.shift_back)
        app.keyboardmanager.bindKeyDown(keyname='Up', handler=self.zoom_in)
        app.keyboardmanager.bindKeyDown(keyname='Down', handler=self.zoom_out)



        # axes
        self.time_axis = axis.TimeAxisNode(size=(self.width - 100, 20), pos=(50, self.height - 40), parent=self,
                                           data_range=global_values.total_range, unit="ms")
        self.y_axis = axis.AxisNode(size=(libavg.app.instance._resolution[1] - 80, 30), pos=(25, 0), parent=self,
                                    vertical=True, data_range=global_values.x_range, unit="cm")

    def onFrame(self):
        if global_values.update_interval_range():
            for visualization in self.visualizations:
                visualization.createLine()

            true_range = global_values.total_range[1] - global_values.total_range[0]
            offset = global_values.get_interval_range()[0]  # self.shift_current * true_range
            self.time_axis.update(visualization.start * true_range, visualization.end * true_range, offset)

    def draw_line(self, p1, p2, color, thickness, last_thickness, opacity):
        return libavg.LineNode(pos1=p1, pos2=p2, color=color, strokewidth=thickness, parent=self)

    def draw_line_variable_thickness(self, color, opacity, p1, p2, p3, p4, thickness1, thickness2, thickness3, thickness4, newNode=True):
        start_points = calculate_line_intersection(p1, p2, p3, thickness1, thickness2, thickness3)
        end_points = calculate_line_intersection(p2, p3, p4, thickness2, thickness3, thickness4)
        if newNode:
            return libavg.PolygonNode(pos=[start_points[0], end_points[0], end_points[1], start_points[1]], opacity=opacity, color=color, parent=self)
        return [start_points[0], end_points[0], end_points[1], start_points[1]]

    def zoom_in(self):
        global_values.zoom_in_at(0.5)

    def zoom_out(self):
        global_values.zoom_out_at(0.5)

    def shift_back(self):
        global_values.shift_time(False)

    def shift_forward(self):
        global_values.shift_time(True)

    def onMouseWheel(self, event):
        if event.motion.y > 0:
            global_values.zoom_in_at(event.pos[0] / self.resolution[0])
        else:
            global_values.zoom_out_at(event.pos[0] / self.resolution[0])


def calculate_line_intersection(p1, p2_selected, p3, thickness1, thickness2_selected, thickness3):
    thickness1 *= 0.5
    thickness2_selected *= 0.5
    thickness3 *= 0.5
    vector_1 = (p2_selected[0] - p1[0], p2_selected[1] - p1[1])
    vector_2 = (p3[0] - p2_selected[0], p3[1] - p2_selected[1])
    vector_length_1 = math.sqrt(vector_1[0] * vector_1[0] + vector_1[1] * vector_1[1])
    vector_length_2 = math.sqrt(vector_2[0] * vector_2[0] + vector_2[1] * vector_2[1])
    try:
        normalized_vector_1 = (vector_1[0] / vector_length_1, vector_1[1] / vector_length_1)
        normalized_vector_2 = (vector_2[0] / vector_length_2, vector_2[1] / vector_length_2)
    except:
        normalized_vector_1 = (0, 1)
        normalized_vector_2 = (0, 1)

    left_1 = (p1[0] - normalized_vector_1[1] * thickness1, p1[1] + normalized_vector_1[0] * thickness1)
    left2_1 = (p2_selected[0] - normalized_vector_1[1] * thickness2_selected, p2_selected[1] + normalized_vector_1[0] * thickness2_selected)
    left2_2 = (p2_selected[0] - normalized_vector_2[1] * thickness2_selected, p2_selected[1] + normalized_vector_2[0] * thickness2_selected)
    left_3 = (p3[0] - normalized_vector_2[1] * thickness3, p3[1] + normalized_vector_2[0] * thickness3)

    right_1 = (p1[0] + normalized_vector_1[1] * thickness1, p1[1] - normalized_vector_1[0] * thickness1)
    right2_1 = (p2_selected[0] + normalized_vector_1[1] * thickness2_selected, p2_selected[1] - normalized_vector_1[0] * thickness2_selected)
    right2_2 = (p2_selected[0] + normalized_vector_2[1] * thickness2_selected, p2_selected[1] - normalized_vector_2[0] * thickness2_selected)
    right_3 = (p3[0] + normalized_vector_2[1] * thickness3, p3[1] - normalized_vector_2[0] * thickness3)

    intersection_point_1 = Util.line_intersection((left_1, left2_1), (left2_2, left_3))
    intersection_point_2 = Util.line_intersection((right_1, right2_1), (right2_2, right_3))
    distance_1 = Util.get_length((intersection_point_1[0] - tuple(p2_selected)[0], intersection_point_1[1] - tuple(p2_selected)[1]))

    if (distance_1 > 12):
        return [left2_2, right2_2]

    return [intersection_point_1, intersection_point_2]


def make_variable_line_thickness_polygon(p1, p2, thickness_1, thickness_2):
    polygon = []
    polygon.append((p1[0], p1[1] + thickness_1 / float(2)))
    polygon.append((p2[0], p2[1] + thickness_2 / float(2)))
    polygon.append((p2[0], p2[1] - thickness_2 / float(2)))
    polygon.append((p1[0], p1[1] - thickness_1 / float(2)))
    return polygon
