import math

from libavg import app, avg

import libavg
import Util
import User
import Line_Visualization
import Time_Frame
import global_values
import axis

class main_drawer(app.MainDiv):
    last_time = 0
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

        # main_drawer Div has margin to all sides of application window
        margin = global_values.APP_MARGIN
        # ratio for distributing visualizations across application
        ratio = 0.7
        # padding
        pad = global_values.APP_PADDING

        self.pos = (margin, margin)
        self.resolution = (libavg.app.instance._resolution[0] - 2*margin, libavg.app.instance._resolution[1] - 2*margin)
        
        self.menu_width = 500
        self.menu_height = 200
        
        # to color background
        libavg.RectNode(parent=self, pos=(0, 0), size=self.resolution,
                        strokewidth=0, fillcolor=global_values.COLOR_BLACK, fillopacity=1)

        for userid in range(1, 5):
            user = User.User(userid)

        self.main_visualization = Line_Visualization.Line_Visualization(parent=self, size=(self.resolution[0] - self.menu_width, self.resolution[1]-100),
                                                                   pos=(0, 0),
                                                                   data_type_x=Line_Visualization.DATA_TIME,
                                                                   data_type_y=Line_Visualization.DATA_POSITION_X,
                                                                   data_type_thickness=Line_Visualization.DATA_POSITION_Z,
                                                                   data_type_opacity=Line_Visualization.DATA_POSITION_Z,
                                                                   show_bottom_axis=True)
        Time_Frame.main_time_frame.subscribe(self.main_visualization)



        self.wall_visualization = Line_Visualization.Line_Visualization(parent=self, size=(self.menu_width, (self.resolution[1]-self.menu_height)/2),
                                                                   pos=(self.resolution[0]-self.menu_width, 0),
                                                                   data_type_x=Line_Visualization.DATA_POSITION_X,
                                                                   data_type_y=Line_Visualization.DATA_POSITION_Y,
                                                                   data_type_thickness=1.4,
                                                                   data_type_opacity=0.01,
                                                                   show_bottom_axis=True)
        Time_Frame.main_time_frame.subscribe(self.wall_visualization)

        self.room_visualization = Line_Visualization.Line_Visualization(parent=self, size=(self.menu_width, (self.resolution[1]-self.menu_height)/2),
                                                                   pos=(self.resolution[0]-self.menu_width, (self.wall_visualization.pos[1] + self.wall_visualization.height)),
                                                                   data_type_x=Line_Visualization.DATA_POSITION_X,
                                                                   data_type_y=Line_Visualization.DATA_POSITION_Z,
                                                                   data_type_thickness=1.4,
                                                                   data_type_opacity=0.01,
                                                                   show_bottom_axis=False)
        Time_Frame.main_time_frame.subscribe(self.room_visualization)

        self.subscribe(avg.Node.MOUSE_WHEEL, self.onMouseWheel)
        app.keyboardmanager.bindKeyDown(keyname='Right', handler=self.shift_forward)
        app.keyboardmanager.bindKeyDown(keyname='Left', handler=self.shift_back)
        app.keyboardmanager.bindKeyDown(keyname='Up', handler=self.zoom_in)
        app.keyboardmanager.bindKeyDown(keyname='Down', handler=self.zoom_out)

    def onFrame(self):
        Time_Frame.main_time_frame.update_interval_range()

    def draw_line(self, p1, p2, color, thickness, last_thickness, opacity):
        return libavg.LineNode(pos1=p1, pos2=p2, color=color, strokewidth=thickness, parent=self)

    def draw_line_variable_thickness(self, color, opacity, p1, p2, p3, p4, thickness1, thickness2, thickness3, thickness4, newNode=True):
        start_points = calculate_line_intersection(p1, p2, p3, thickness1, thickness2, thickness3)
        end_points = calculate_line_intersection(p2, p3, p4, thickness2, thickness3, thickness4)
        if newNode:
            return libavg.PolygonNode(pos=[start_points[0], end_points[0], end_points[1], start_points[1]], opacity=opacity, color=color, parent=self)
        return [start_points[0], end_points[0], end_points[1], start_points[1]]

    def zoom_in(self):
        Time_Frame.main_time_frame.zoom_in_at(0.5)

    def zoom_out(self):
        Time_Frame.main_time_frame.zoom_out_at(0.5)

    def shift_back(self):
        Time_Frame.main_time_frame.shift_time(False)

    def shift_forward(self):
        Time_Frame.main_time_frame.shift_time(True)

    def onMouseWheel(self, event):
        if event.motion.y > 0:
            Time_Frame.main_time_frame.zoom_in_at((event.pos[0]-axis.AXIS_THICKNESS) / (self.main_visualization.width-axis.AXIS_THICKNESS))
        else:
            Time_Frame.main_time_frame.zoom_out_at((event.pos[0]-axis.AXIS_THICKNESS) / (self.main_visualization.width-axis.AXIS_THICKNESS))


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

    return [intersection_point_1, intersection_point_2]


def make_variable_line_thickness_polygon(p1, p2, thickness_1, thickness_2):
    polygon = []
    polygon.append((p1[0], p1[1] + thickness_1 / float(2)))
    polygon.append((p2[0], p2[1] + thickness_2 / float(2)))
    polygon.append((p2[0], p2[1] - thickness_2 / float(2)))
    polygon.append((p1[0], p1[1] - thickness_1 / float(2)))
    return polygon
