import User
import database
import global_values
import Util
import axis
import Time_Frame
import libavg
import Variable_Width_Line

DATA_POSITION_X = 0
DATA_POSITION_Y = 1
DATA_POSITION_Z = 2
DATA_TIME = 3
DATA_VIEWPOINT_X = 4
DATA_VIEWPOINT_Y = 5
DATA_TOUCH_X = 6
DATA_TOUCH_Y = 7

VIS_X = 0
VIS_Y = 1
VIS_THICKNESS = 2
VIS_OPACITY = 3


class Line_Visualization(libavg.DivNode):
    canvasObjects = []
    samples_per_pixel = 1
    parent = 0
    start = 0
    end = 1

    def __init__(self, parent, data_type_x, data_type_y, data_type_thickness, data_type_opacity, **kwargs):
        super(Line_Visualization, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.crop = True

        self.data_type_x = data_type_x
        self.data_type_y = data_type_y
        self.data_type_thickness = data_type_thickness
        self.data_type_opacity = data_type_opacity

        self.data_div = libavg.DivNode(pos=(axis.AXIS_THICKNESS, 0), size=(self.width - axis.AXIS_THICKNESS, self.height - axis.AXIS_THICKNESS), parent=self, crop=True)

        # rect for coloured border and background
        libavg.RectNode(pos=(0, 0), size=self.size, parent=self,
                        strokewidth=0, fillopacity=0, fillcolor=global_values.COLOR_FOREGROUND)

        # axes
        self.y_axis = axis.AxisNode(size=(axis.AXIS_THICKNESS, self.data_div.height), parent=self, sensitive=False, data_range=global_values.x_range, unit="cm", pos=(0, 0))

        self.time_axis = axis.TimeAxisNode(size=(self.width, self.data_div.width), parent=self, data_range=Time_Frame.total_range, unit="ms", pos=(0, self.data_div.height))
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
            points = []
            widths = []
            opacities = []
            samplecount = 100
            if self.data_type_x == DATA_TIME:
                samplecount = int(self.data_div.width * global_values.samples_per_pixel) + 1
            if self.data_type_y == DATA_TIME:
                samplecount = int(self.data_div.height * global_values.samples_per_pixel) + 1
            for sample in range(samplecount):
                if len(user.head_positions) == 0:
                    continue
                posindex = int(
                    len(user.head_positions) * sample * (self.end - self.start) / float(
                        samplecount) + self.start * len(user.head_positions))
                current_position = []
                head_position_averaged = user.get_head_position_averaged(posindex)

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

                    if data_type == DATA_POSITION_X:
                        data = (head_position_averaged[0] - database.min_x) / float(database.max_x - database.min_x)
                    if data_type == DATA_POSITION_Y:
                        data = (head_position_averaged[1] - database.min_y) / float(database.max_y - database.min_y)
                    if data_type == DATA_POSITION_Z:
                        data = (head_position_averaged[2] - database.min_z) / float(database.max_z - database.min_z)

                    if data_type == DATA_TIME:
                        data = float(sample) / float(samplecount)

                    if data_type == DATA_VIEWPOINT_X:
                        print "not done yet"
                        # TODO
                    if data_type == DATA_VIEWPOINT_Y:
                        print "not done yet"
                        # TODO

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

                    if i == VIS_THICKNESS:
                        data = 1 + pow(data, 3) * 60

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
                    Variable_Width_Line.Variable_Width_Line(points=points, widths=widths, opacities=opacities, parent=self.data_div,
                                                            color=Util.get_user_color_as_hex(userid, 1)))

    def draw(self):

        for user in User.users:
            for point in user.head_positions:
                None
