import User
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

DATA_POSITION = [DATA_POSITION_X, DATA_POSITION_Y, DATA_POSITION_Z]
DATA_VIEWPOINT = [DATA_VIEWPOINT_X, DATA_VIEWPOINT_Y]

VIS_X = 0
VIS_Y = 1
VIS_THICKNESS = 2
VIS_OPACITY = 3


class Line_Visualization(libavg.DivNode):
    start = 0
    end = 1

    def __init__(self, parent, data_type_x, data_type_y, data_type_thickness, data_type_opacity, top_axis=False,
                 invert_x=False, invert_y=False, name="", **kwargs):
        super(Line_Visualization, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.crop = False

        self.data_type_x = data_type_x
        self.canvasObjects = []
        self.data_type_y = data_type_y
        self.data_type_thickness = data_type_thickness
        self.data_type_opacity = data_type_opacity
        custom_label_offset = -1

        self.data_types = [self.data_type_x, self.data_type_y, self.data_type_opacity, self.data_type_thickness]


        # rect for coloured border and background
        self.background_rect = libavg.RectNode(pos=(axis.AXIS_THICKNESS, 0),
                                               size=(self.width - axis.AXIS_THICKNESS, self.height - axis.AXIS_THICKNESS),
                                               parent=self, strokewidth=1, fillopacity=1,
                                               color=global_values.COLOR_FOREGROUND,
                                               fillcolor=global_values.COLOR_BLACK)

        # div for visualization data
        self.data_div = libavg.DivNode(pos=(axis.AXIS_THICKNESS, 0),
                                       size=(self.width - axis.AXIS_THICKNESS, self.height - axis.AXIS_THICKNESS),
                                       parent=self, crop=True)

        # user divs to distinguish MeshNodes in data_div by user (user_divs are initialized as self.data_div's)
        self.user_divs = []
        for i in range((len(User.users))):
            self.user_divs.append(libavg.DivNode(pos=(0, 0), parent=self.data_div, crop=True, size=self.size))

        # y-axis
        if data_type_y == DATA_TIME:
            self.y_axis = axis.TimeAxisNode(pos=(0, 0), parent=self, size=(axis.AXIS_THICKNESS, self.data_div.height),
                                            data_range=Time_Frame.total_range, unit="ms", inverted=invert_y)
        else:
            data_range = [0, 10]
            unit = ""
            # set data_range according to data input
            if data_type_y == DATA_POSITION_X:
                data_range = global_values.x_range
                unit = "cm"
                custom_label_offset = 23
            elif data_type_y == DATA_POSITION_Y:
                data_range = global_values.y_range
                unit = "cm"
            elif data_type_y == DATA_POSITION_Z:
                data_range = global_values.z_range
                unit = "cm"
            elif data_type_y == DATA_TOUCH_Y:
                data_range = global_values.y_touch_range
                unit = "px"
            elif data_type_y == DATA_TOUCH_X:
                data_range = global_values.x_touch_range
                unit = "px"
            elif data_type_y == DATA_VIEWPOINT_X:
                data_range = global_values.x_wall_range
                unit = "cm"
            elif data_type_y == DATA_VIEWPOINT_Y:
                data_range = global_values.y_wall_range
                unit = "cm"

            if custom_label_offset == -1:
                self.y_axis = axis.AxisNode(pos=(0, 0), size=(axis.AXIS_THICKNESS, self.data_div.height), parent=self,
                                            sensitive=True, data_range=data_range, unit=unit, hide_rims=True,
                                            inverted=invert_y)
            else:
                self.y_axis = axis.AxisNode(pos=(0, 0), size=(axis.AXIS_THICKNESS, self.data_div.height), parent=self,
                                            sensitive=True, data_range=data_range, unit=unit, hide_rims=True,
                                            inverted=invert_y, label_offset=custom_label_offset)

        # x-axis
        x_axis_pos = (axis.AXIS_THICKNESS, self.data_div.height)
        if self.data_type_x == DATA_TIME:
            self.x_axis = axis.TimeAxisNode(pos=x_axis_pos, parent=self, unit="ms", data_range=Time_Frame.total_range,
                                            size=(self.data_div.width, axis.AXIS_THICKNESS), inverted=invert_x)
        else:
            # set data_range according to data input
            if data_type_x == DATA_POSITION_X:
                data_range = global_values.x_range
            elif data_type_x == DATA_POSITION_Y:
                data_range = global_values.y_range
            elif data_type_x == DATA_POSITION_Z:
                data_range = global_values.z_range
            elif data_type_x == DATA_TOUCH_Y:
                data_range = global_values.y_touch_range
            elif data_type_x == DATA_TOUCH_X:
                data_range = global_values.x_touch_range
            elif data_type_x == DATA_VIEWPOINT_X:
                data_range = global_values.x_range
            elif data_type_x == DATA_VIEWPOINT_Y:
                data_range = global_values.y_wall_range
            self.x_axis = axis.AxisNode(pos=x_axis_pos, size=(self.data_div.width, axis.AXIS_THICKNESS), hide_rims=True,
                                        sensitive=True, parent=self, data_range=data_range, unit="cm",
                                        top_axis=top_axis, inverted=invert_x)

        if top_axis:
            self.x_axis.pos = (axis.AXIS_THICKNESS, 0)

        self.createLine()

        # name
        libavg.WordsNode(pos=(axis.AXIS_THICKNESS + global_values.APP_PADDING, global_values.APP_PADDING), parent=self,
                         color=global_values.COLOR_FOREGROUND, text=name, sensitive=False, alignment="left")

    # make start and end values in 0..1
    def update_time_frame(self, interval):
        start_orig = self.start
        end_orig = self.end
        self.start = interval[0] / (Time_Frame.total_range[1] - Time_Frame.total_range[0])
        self.end = interval[1] / (Time_Frame.total_range[1] - Time_Frame.total_range[0])
        if self.start != start_orig or self.end != end_orig:
            self.createLine()

    def createLine(self):
        userid = -1
        for user in User.users:
            userid += 1
            if user.selected:
                points = []
                widths = []
                opacities = []
                samplecount = 100
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

                    if any(data_type in self.data_types for data_type in DATA_POSITION):
                        head_position_averaged = user.get_head_position_averaged(posindex)
                    if any(data_type in self.data_types for data_type in DATA_VIEWPOINT):
                        view_point_averaged = user.get_view_point_averaged(posindex)

                    for i in range(4):
                        data = 0

                        if i == VIS_X:
                            data_type = self.data_type_x
                        elif i == VIS_Y:
                            data_type = self.data_type_y
                        elif i == VIS_THICKNESS:
                            data_type = self.data_type_thickness
                        elif i == VIS_OPACITY:
                            data_type = self.data_type_opacity

                        if data_type > 0:
                            data = data_type

                        elif data_type == DATA_POSITION_X:
                            data = (head_position_averaged[0] - global_values.x_range[0]) / float(global_values.x_range[1] - global_values.x_range[0])
                            if i == VIS_Y:
                                data = 1 - data
                        elif data_type == DATA_POSITION_Y:
                            data = (head_position_averaged[1] - global_values.y_range[0]) / float(global_values.y_range[1] - global_values.y_range[0])
                        elif data_type == DATA_POSITION_Z:
                            data = (head_position_averaged[2] - global_values.z_range[0]) / float(global_values.z_range[1] - global_values.z_range[0])

                        elif data_type == DATA_TIME:
                            data = float(sample) / float(max(1, samplecount - 1))

                        elif data_type == DATA_VIEWPOINT_X:
                            data = (view_point_averaged[0] - global_values.x_wall_range[0]) / float(global_values.x_wall_range[1] - global_values.x_wall_range[0])
                        elif data_type == DATA_VIEWPOINT_Y:
                            data = (view_point_averaged[1] - global_values.y_wall_range[0]) / float(global_values.y_wall_range[1] - global_values.y_wall_range[0])
                            data = 1 - data


                        elif data_type == DATA_TOUCH_X:
                            print "not working yet"
                            # touch_x = (user.touches[posindex][0]-database.min_touch_x)/float(database.max_touch_x-database.min_touch_x)

                        elif data_type == DATA_TOUCH_Y:
                            print "not working yet"
                            # touch_y = (user.touches[posindex][1]-database.min_touch_y)/float(database.max_touch_y-database.min_touch_y)
                            # touch_time = (user.touches[posindex][2]-database.min_time)/float(database.max_time-database.min_time)

                        if i == VIS_X:
                            data *= self.data_div.width

                        elif i == VIS_Y:
                            data *= self.data_div.height

                        elif i == VIS_THICKNESS and data_type <= 0:
                            data = calculate_thickness(data, self)

                        elif i == VIS_OPACITY:
                            data = calculate_opacity(data)
                        # x or y value of the visualization depending on i being
                        current_position.append(data)

                    points.append((current_position[VIS_X], current_position[VIS_Y]))
                    widths.append(current_position[VIS_THICKNESS])
                    opacities.append(current_position[VIS_OPACITY])

                if len(self.canvasObjects) > userid:
                    userline = self.canvasObjects[userid]
                    userline.set_values(points, widths, opacities)
                else:
                    self.canvasObjects.append(
                        Variable_Width_Line.Variable_Width_Line(points=points, widths=widths, opacities=opacities,
                                                                userid=userid, parent=self.user_divs[userid]))


def calculate_thickness(data, div):
    return 1.4 + pow(data, 3) * (min(div.width, div.height)/12)


def calculate_opacity(data):
    return 0.05 + 0.95*pow((1 - data), 2)
