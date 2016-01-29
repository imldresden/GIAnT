import User
import database
import global_values
import axis
import Time_Frame
import libavg
import Variable_Width_Line

DATA_POSITION_X = 0
DATA_POSITION_Y = -1
DATA_POSITION_Z = -2
DATA_TIME = -3
DATA_VIEWPOINT_X = -4
DATA_VIEWPOINT_Y = -5
DATA_TOUCH_X = -6
DATA_TOUCH_Y = -7

VIS_X = 0
VIS_Y = 1
VIS_THICKNESS = 2
VIS_OPACITY = 3


class Line_Visualization(libavg.DivNode):
    start = 0
    end = 1

    def __init__(self, parent, data_type_x, data_type_y, data_type_thickness, data_type_opacity, show_bottom_axis=True, **kwargs):
        super(Line_Visualization, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.crop = False

        #here the size is first increased, so that it later can be decreased again (around line 82), effectively hiding the bottom axis but still showing its grid
        if not show_bottom_axis:
            pass  # self.size = (self.width, self.height+axis.AXIS_THICKNESS)

        self.data_type_x = data_type_x
        self.canvasObjects = []
        self.data_type_y = data_type_y
        self.data_type_thickness = data_type_thickness
        self.data_type_opacity = data_type_opacity

        # rect for coloured border and background
        self.background_rect = libavg.RectNode(pos=(axis.AXIS_THICKNESS, 0),
                                               size=(self.width - axis.AXIS_THICKNESS, self.height - axis.AXIS_THICKNESS),
                                               parent=self, strokewidth=1, fillopacity=1,
                                               color=global_values.COLOR_BACKGROUND,
                                               fillcolor=global_values.COLOR_BACKGROUND)

        # div for visualization data
        self.data_div = libavg.DivNode(pos=(axis.AXIS_THICKNESS, 0),
                                       size=(self.width - axis.AXIS_THICKNESS, self.height - axis.AXIS_THICKNESS),
                                       parent=self, crop=True)

        # user divs to distinguish MeshNodes in data_div by user (user_divs are initialized as self.data_div's)
        self.user_divs = []
        for i in range((len(User.users))):
            self.user_divs.append(libavg.DivNode(pos=(0, 0), parent=self.data_div, crop=True, size=self.size))

        # axes
        if data_type_y == DATA_TIME:
            self.y_axis = axis.TimeAxisNode(pos=(0, 0), parent=self, size=(axis.AXIS_THICKNESS, self.data_div.height), data_range=Time_Frame.total_range, unit="ms")

        else:
            data_range = [0, 10]
            unit = ""
            # set data_range according to data input
            if data_type_y == DATA_POSITION_X:
                data_range = global_values.x_range
                unit = "cm"
            if data_type_y == DATA_POSITION_Y:
                data_range = global_values.y_range
                unit = "cm"
            if data_type_y == DATA_POSITION_Z:
                data_range = global_values.z_range
                unit = "cm"
            if data_type_y == DATA_TOUCH_Y:
                data_range = global_values.y_touch_range
                unit = "px"
            if data_type_y == DATA_TOUCH_X:
                data_range = global_values.x_touch_range
                unit = "px"
            if data_type_y == DATA_VIEWPOINT_X:
                data_range = global_values.x_wall_range
            if data_type_y == DATA_VIEWPOINT_Y:
                data_range = global_values.y_wall_range

            self.y_axis = axis.AxisNode(pos=(0, 0), size=(axis.AXIS_THICKNESS, self.data_div.height), hide_rims=True, parent=self, sensitive=True, data_range=data_range, unit=unit)

        x_axis_pos = (axis.AXIS_THICKNESS, self.data_div.height)

        if self.data_type_x == DATA_TIME:
            self.x_axis = axis.TimeAxisNode(pos=x_axis_pos, parent=self, size=(self.data_div.width, axis.AXIS_THICKNESS), data_range=Time_Frame.total_range,
                                            unit="ms")
        else:
            # set data_range according to data input
            if data_type_x == DATA_POSITION_X:
                data_range = global_values.x_range
            if data_type_x == DATA_POSITION_Y:
                data_range = global_values.y_range
            if data_type_x == DATA_POSITION_Z:
                data_range = global_values.z_range
            if data_type_x == DATA_TOUCH_Y:
                data_range = global_values.y_touch_range
            if data_type_x == DATA_TOUCH_X:
                data_range = global_values.x_touch_range
            if data_type_x == DATA_VIEWPOINT_X:
                data_range = global_values.x_wall_range
            if data_type_x == DATA_VIEWPOINT_Y:
                data_range = global_values.y_wall_range
            self.x_axis = axis.AxisNode(pos=x_axis_pos,
                                        size=(self.data_div.width, axis.AXIS_THICKNESS),
                                        hide_rims=True, sensitive=True,
                                        parent=self, data_range=data_range, unit="cm")


        self.createLine()

    # make start and end values in 0..1
    def update_time_frame(self, interval):
        self.start = interval[0] / (Time_Frame.total_range[1] - Time_Frame.total_range[0])
        self.end = interval[1] / (Time_Frame.total_range[1] - Time_Frame.total_range[0])
        self.createLine()

    def createLine(self):
        userid = -1
        for user in User.users:
            userid += 1
            if user.selected:
                points = []
                widths = []
                opacities = []
                samplecount = 200
                if self.data_type_x == DATA_TIME:
                    samplecount = int(self.data_div.width * global_values.samples_per_pixel) + 1
                if self.data_type_y == DATA_TIME:
                    samplecount = int(self.data_div.height * global_values.samples_per_pixel) + 1
                for sample in range(samplecount):
                    if len(user.head_positions_integral) == 0:
                        continue
                    posindex = int(
                        len(user.head_positions_integral) * sample * (self.end - self.start) / float(
                            samplecount) + self.start * len(user.head_positions_integral))
                    current_position = []
                    if self.data_type_x in [DATA_POSITION_X, DATA_POSITION_Y, DATA_POSITION_Z] or self.data_type_y in [DATA_POSITION_X, DATA_POSITION_Y, DATA_POSITION_Z]:
                        head_position_averaged = user.get_head_position_averaged(posindex)
                    if self.data_type_x in [DATA_VIEWPOINT_X, DATA_VIEWPOINT_Y] or self.data_type_y in [DATA_VIEWPOINT_X, DATA_VIEWPOINT_Y]:
                        view_point_averaged = user.get_view_point_averaged(posindex)

                    for i in range(4):
                        data = 0

                        if i == VIS_X:
                            data_type = self.data_type_x
                        if i == VIS_Y:
                            data_type = self.data_type_y
                        if i == VIS_THICKNESS:
                            data_type = self.data_type_thickness
                        if i == VIS_OPACITY:
                            data_type = self.data_type_opacity

                        if data_type > 0:
                            data = data_type

                        if data_type == DATA_POSITION_X:
                            data = (head_position_averaged[0] - global_values.x_range[0]) / float(global_values.x_range[1] - global_values.x_range[0])
                        if data_type == DATA_POSITION_Y:
                            data = (head_position_averaged[1] - global_values.y_range[0]) / float(global_values.y_range[1] - global_values.y_range[0])
                        if data_type == DATA_POSITION_Z:
                            data = (head_position_averaged[2] - global_values.z_range[0]) / float(global_values.x_range[1] - global_values.z_range[0])

                        if data_type == DATA_TIME:
                            data = float(sample) / float(max(1, samplecount - 1))

                        if data_type == DATA_VIEWPOINT_X:
                            data = (view_point_averaged[0]-global_values.x_wall_range[0]) / float(global_values.x_wall_range[1]-global_values.x_wall_range[0])
                        if data_type == DATA_VIEWPOINT_Y:
                            data = (view_point_averaged[1]-global_values.y_wall_range[0]) / float(global_values.y_wall_range[1]-global_values.y_wall_range[0])

                        if data_type == DATA_TOUCH_X:
                            print "not working yet"
                            # touch_x = (user.touches[posindex][0]-database.min_touch_x)/float(database.max_touch_x-database.min_touch_x)

                        if data_type == DATA_TOUCH_Y:
                            print "not working yet"
                            # touch_y = (user.touches[posindex][1]-database.min_touch_y)/float(database.max_touch_y-database.min_touch_y)
                            # touch_time = (user.touches[posindex][2]-database.min_time)/float(database.max_time-database.min_time)

                        if i == VIS_X:
                            data *= self.data_div.width

                        if i == VIS_Y:
                            data *= self.data_div.height

                        if i == VIS_THICKNESS and data_type <= 0:
                            data = calculate_thickness(data, self)

                        if i == VIS_OPACITY:
                            data = (1 - data)
                        # x or y value of the visualization depending on i being
                        current_position.append(data)

                    points.append((current_position[VIS_X], current_position[VIS_Y]))
                    widths.append(current_position[VIS_THICKNESS])
                    opacities.append(current_position[VIS_OPACITY])
                    '''
                    if last_position == 0:
                        last_position = current_position
                    else:
                        if len(self.canvasObjects) <= userid:
                            user_objects.append(
                                Draw.main_drawer.draw_line(self.parent, tuple(current_position), tuple(last_position),
                                                         global_values.get_color_as_hex(userid, 1), thickness, thickness, opacity))
                        else:
                            if len(self.canvasObjects[userid]) > i:
                                self.canvasObjects[userid][i].pos1 = current_position
                                self.canvasObjects[userid][i].pos2 = last_position
                                self.canvasObjects[userid][i].strokewidth = thickness
                                self.canvasObjects[userid][i].opacity = opacity
                        last_position = current_position
                    '''

                if len(self.canvasObjects) > userid:
                    userline = self.canvasObjects[userid]
                    userline.set_values(points, widths, opacities)
                else:
                    self.canvasObjects.append(
                        Variable_Width_Line.Variable_Width_Line(points=points, widths=widths, opacities=opacities,
                                                                userid=userid, parent=self.user_divs[userid]))

    def draw(self):

        for user in User.users:
            for point in user.head_positions:
                None

def calculate_thickness(data, div):
     return 1.4 + pow(data, 4) * (min(div.width, div.height) / 3)