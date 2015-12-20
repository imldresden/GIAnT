from libavg import app, avg
import libavg
import axis
import User
import Util
import Visualization
import time
import math


class main_drawer(app.MainDiv):
    last_time = 0
    visualizations = []
    resolution = (1920, 1000)
    viewport_change_duration = 0.3

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

    def onInit(self):
        self.resolution = libavg.app.instance._resolution
        libavg.RectNode(pos=(0, 0), size=self.resolution, fillcolor='ffffff', parent=self)
        for userid in range(1, 5):
            user = User.User(userid)
        self.visualizations.append(Visualization.Visualization(self, self.resolution, (100, 100)))
        self.subscribe(avg.Node.MOUSE_WHEEL, self.onMouseWheel)
        app.keyboardmanager.bindKeyDown(keyname='Right', handler=self.shift_forward)
        app.keyboardmanager.bindKeyDown(keyname='Left', handler=self.shift_back)

        # axes
        axis.AxisNode(size=(self.width, 50), pos=(0, 0), parent=self)
        axis.AxisNode(size=(self.width, 50), pos=(0, 0), parent=self, vertical=True)

    def onFrame(self):
        # print 1 / (time.time() - self.last_time)  # FPS
        self.last_time = time.time()
        if self.zoom_change_starttime != 0 or self.shift_change_starttime != 0:
            if self.zoom_change_starttime != 0:
                if self.zoom_change_progress == 1:
                    self.zoom_last = self.zoom_target
                    self.zoom_change_starttime = 0
                    return

                self.zoom_change_progress = (time.time() - self.zoom_change_starttime) / self.viewport_change_duration
                self.zoom_change_progress = min(1, self.zoom_change_progress)

                self.zoom_current = self.zoom_last * (1 - self.zoom_change_progress) + self.zoom_target * self.zoom_change_progress

            if self.shift_change_starttime != 0:
                if self.shift_change_progress == 1:
                    self.shift_last = self.shift_target
                    self.shift_change_starttime = 0
                    return

                self.shift_change_progress = (time.time() - self.shift_change_starttime) / self.viewport_change_duration
                self.shift_change_progress = min(1, self.shift_change_progress)

                self.shift_current = self.shift_last * (1 - self.shift_change_progress) + self.shift_target * self.shift_change_progress
            for visualization in self.visualizations:
                visualization.start = (self.zoom_current - 1) * self.shift_current
                visualization.end = 1 - (self.zoom_current - 1) * (1 - self.shift_current)
                visualization.createLine()

    def draw_line(self, p1, p2, color, thickness, last_thickness, opacity):
        return libavg.LineNode(pos1=p1, pos2=p2, color=color, strokewidth=thickness, parent=self)

    def draw_line_variable_thickness(self, color, opacity, p1, p2, p3, p4, thickness1, thickness2, thickness3, thickness4, newNode=True):
        start_points = calculate_line_intersection(p1, p2, p3, thickness1, thickness2, thickness3)
        end_points = calculate_line_intersection(p2, p3, p4, thickness2, thickness3, thickness4)
        if newNode:
            return libavg.PolygonNode(pos=[start_points[0], end_points[0], end_points[1], start_points[1]], opacity=opacity, color=color, parent=self)
        return [start_points[0], end_points[0], end_points[1], start_points[1]]

    def shift_back(self):
        try:
            self.shift_last = self.shift_current
            self.shift_target = self.shift_target - pow(2 - self.zoom_target, 1.5)
            self.shift_target = min(1, max(0, self.shift_target))
            self.shift_change_starttime = time.time()
            self.shift_change_progress = 0
        except:
            None

    def shift_forward(self):
        try:
            self.shift_last = self.shift_current
            self.shift_target = self.shift_target + pow(2 - self.zoom_target, 1.5)
            self.shift_target = min(1, max(0, self.shift_target))
            self.shift_change_starttime = time.time()
            self.shift_change_progress = 0
        except:
            None

    def onMouseWheel(self, event):
        if event.motion.y > 0:
            self.zoomIn()
        else:
            self.zoomOut()

    def zoomIn(self):
        self.zoom_last = self.zoom_current
        # self.zoom_target += (1.5 - self.zoom_target) * self.zoom_amount
        self.zoom_target += (2 - self.zoom_target) / float(5)
        self.zoom_target = min(2, max(1, self.zoom_target))
        self.zoom_change_starttime = time.time()
        self.zoom_change_progress = 0

    def zoomOut(self):
        self.zoom_last = self.zoom_current
        strength = (1.5 - self.zoom_target) * self.zoom_amount
        # self.zoom_target -= self.zoom_target / ((1 / strength) + 1)
        self.zoom_target -= (2 - self.zoom_target) / float(4)
        self.zoom_target = min(2, max(1, self.zoom_target))
        self.zoom_change_starttime = time.time()
        self.zoom_change_progress = 0


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
        normalized_vector_1 = (0,1)
        normalized_vector_2 = (0,1)

    left_1 = (p1[0] - normalized_vector_1[1] * thickness1, p1[1] + normalized_vector_1[0] * thickness1)
    left2_1 = (p2_selected[0] - normalized_vector_1[1] * thickness2_selected, p2_selected[1] + normalized_vector_1[0] * thickness2_selected)
    left2_2 = (p2_selected[0] - normalized_vector_2[1] * thickness2_selected, p2_selected[1] + normalized_vector_2[0] * thickness2_selected)
    left_3 = (p3[0] - normalized_vector_2[1] * thickness3, p3[1] + normalized_vector_2[0] * thickness3)

    vector_left_1 = (left2_1[0] - left_1[0], left2_1[1] - left_1[1])
    vector_left_2 = (left2_2[0] - left_3[0], left2_2[1] - left_3[1])

    right_1 = (p1[0] + normalized_vector_1[1] * thickness1, p1[1] - normalized_vector_1[0] * thickness1)
    right2_1 = (p2_selected[0] + normalized_vector_1[1] * thickness2_selected, p2_selected[1] - normalized_vector_1[0] * thickness2_selected)
    right2_2 = (p2_selected[0] + normalized_vector_2[1] * thickness2_selected, p2_selected[1] - normalized_vector_2[0] * thickness2_selected)
    right_3 = (p3[0] + normalized_vector_2[1] * thickness3, p3[1] - normalized_vector_2[0] * thickness3)

    vector_right_1 = (right2_1[0] - right_1[0], right2_1[1] - right_1[1])
    vector_right_2 = (right2_2[0] - right_3[0], right2_2[1] - right_3[1])

    intersection_point_1 = Util.line_intersection((left_1, left2_1), (left2_2, left_3))
    intersection_point_2 = Util.line_intersection((right_1, right2_1), (right2_2, right_3))
    return [intersection_point_1, intersection_point_2]


def make_variable_line_thickness_polygon(p1, p2, thickness_1, thickness_2):
    polygon = []
    polygon.append((p1[0], p1[1] + thickness_1 / float(2)))
    polygon.append((p2[0], p2[1] + thickness_2 / float(2)))
    polygon.append((p2[0], p2[1] - thickness_2 / float(2)))
    polygon.append((p1[0], p1[1] - thickness_1 / float(2)))
    return polygon
