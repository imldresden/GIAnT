import User
import global_values
import axis
import Time_Frame
import libavg
import Util
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


class Highlight_Visualization(libavg.DivNode):
    time = 0
    end = 1
    view_line_length = 30

    def __init__(self, parent, data_type_x, data_type_y, data_type_radius, data_type_opacity, draw_view_line, **kwargs):
        super(Highlight_Visualization, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.crop = False

        self.data_type_x = data_type_x
        self.canvasObjects = []
        self.data_type_y = data_type_y
        self.data_type_radius = data_type_radius
        self.data_type_opacity = data_type_opacity

        self.data_types = [self.data_type_x, self.data_type_y, self.data_type_opacity, self.data_type_radius]

        self.draw_view_line = draw_view_line
        self.pos = (self.pos[0] + axis.THICKNESS, self.pos[1])


        # div for visualization data
        self.data_div = libavg.DivNode(pos=(0, 0),
                                       size=(self.width, self.height),
                                       parent=self, crop=True)

        # user divs to distinguish MeshNodes in data_div by user (user_divs are initialized as self.data_div's)
        self.user_divs = []
        for i in range((len(User.users))):
            user_div = libavg.DivNode(pos=(0, 0), parent=self.data_div, crop=True, size=self.size)
            self.user_divs.append(user_div)
            pos = User.users[i].get_head_position_averaged(0)
            look_dir = User.users[i].get_head_orientation(0)
            user_color = Util.get_user_color_as_hex(i, 1)
            libavg.CircleNode(pos=(pos[0], pos[1]), r=(self.size[0] + self.size[1]) / 100, parent=user_div, color=global_values.COLOR_BLACK, fillcolor=user_color, strokewidth=1, fillopacity=1)
            if self.draw_view_line:
                libavg.LineNode(parent=user_div, pos1=(pos[0], pos[1]), pos2=(pos[0], pos[1] + self.view_line_length), color=user_color, strokewidth=3)

        self.set_positions()

    # make time and end values in 0..1
    def update_time_frame(self, interval, draw_lines):
        self.time = Time_Frame.main_time_frame.highlight_time / (Time_Frame.total_range[1] - Time_Frame.total_range[0])
        self.set_positions()

    def set_positions(self):

        for i in range(len(self.user_divs)):
            user_div = self.user_divs[i]
            highlight_time = Util.get_index_from_time_percentage(self.time)
            if self.data_type_x == DATA_POSITION_X:
                if self.data_type_y == DATA_POSITION_Z:
                    new_pos = User.users[i].get_head_position_averaged(highlight_time)
                    new_pos[0] = (new_pos[0] - global_values.x_range[0]) / (global_values.x_range[1] - global_values.x_range[0])
                    new_pos[1] = (new_pos[1] - global_values.y_range[0]) / (global_values.y_range[1] - global_values.y_range[0])
                    new_pos[2] = (new_pos[2] - global_values.z_range[0]) / (global_values.z_range[1] - global_values.z_range[0])
                    pos = (new_pos[0] * self.width, new_pos[2] * self.height)
                    user_div.getChild(0).pos = pos


                if self.draw_view_line:
                    look_dir = User.users[i].get_head_orientation(highlight_time)
                    look_dir = Util.get_look_direction(look_dir[0], look_dir[1])
                    user_div.getChild(1).pos1 = tuple(pos)
                    user_div.getChild(1).pos2 = (pos[0] - self.view_line_length * look_dir[0], pos[1] - self.view_line_length * look_dir[2])

            else:
                if self.data_type_x == DATA_VIEWPOINT_X and self.data_type_y == DATA_VIEWPOINT_Y:
                    new_pos = User.users[i].get_view_point_averaged(highlight_time)
                    new_pos[0] = (new_pos[0] - global_values.x_wall_range[0]) / (global_values.x_wall_range[1] - global_values.x_wall_range[0])
                    new_pos[1] = 1 - (new_pos[1] - global_values.y_wall_range[0]) / (global_values.y_wall_range[1] - global_values.y_wall_range[0])
                    pos = (new_pos[0] * self.width, new_pos[1] * self.height)
                    user_div.getChild(0).pos = pos


        '''
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
                        len(user.head_positions_integral) * sample * (self.end - self.time) / float(
                            samplecount) + self.time * len(user.head_positions_integral))
                    current_position = []

                    if any(data_type in self.data_types for data_type in DATA_POSITION):
                        head_position_averaged = user.get_head_position_averaged(posindex)
                    if any(data_type in self.data_types for data_type in DATA_VIEWPOINT):
                        view_point_averaged = user.get_view_point_averaged(posindex)

                    for i in range(4):
                        data = 0

                        if i == VIS_X:
                            data_type = self.data_type_x
                        if i == VIS_Y:
                            data_type = self.data_type_y
                        if i == VIS_THICKNESS:
                            data_type = self.data_type_radius
                        if i == VIS_OPACITY:
                            data_type = self.data_type_opacity

                        if data_type > 0:
                            data = data_type

                        if data_type == DATA_POSITION_X:
                            data = (head_position_averaged[0] - global_values.x_range[0]) / float(global_values.x_range[1] - global_values.x_range[0])
                        if data_type == DATA_POSITION_Y:
                            data = (head_position_averaged[1] - global_values.y_range[0]) / float(global_values.y_range[1] - global_values.y_range[0])
                        if data_type == DATA_POSITION_Z:
                            data = (head_position_averaged[2] - global_values.z_range[0]) / float(global_values.z_range[1] - global_values.z_range[0])

                        if data_type == DATA_TIME:
                            data = float(sample) / float(max(1, samplecount - 1))

                        if data_type == DATA_VIEWPOINT_X:
                            data = (view_point_averaged[0] - global_values.x_wall_range[0]) / float(global_values.x_wall_range[1] - global_values.x_wall_range[0])
                        if data_type == DATA_VIEWPOINT_Y:
                            data = (view_point_averaged[1] - global_values.y_wall_range[0]) / float(global_values.y_wall_range[1] - global_values.y_wall_range[0])
                            data = 1 - data

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
                                                                userid=userid, parent=self.user_divs[userid]))'''


def calculate_thickness(data, div):
    return 1.4 + pow(data, 3) * (min(div.width, div.height) / 12)


def calculate_opacity(data):
    return 0.05 + 0.95 * pow((1 - data), 2)
