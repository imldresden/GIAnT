import User
import database
import global_values
import axis
import Time_Frame
import libavg
import Variable_Width_Line


class Line_Visualization(libavg.DivNode):
    canvasObjects = []
    samples_per_pixel = 1
    parent = 0
    start = 0
    end = 1

    def __init__(self, parent, size, position,  **kwargs):
        super(Line_Visualization, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.size = size
        self.position = position
        self.parent = parent
        self.createLine()

        # axes
        self.time_axis = axis.TimeAxisNode(size=(self.width - 100, 20), pos=(50, self.height - 40), parent=self,
                                           data_range=Time_Frame.total_range, unit="ms")
        self.y_axis = axis.AxisNode(size=(libavg.app.instance._resolution[1] - 80, 30), pos=(25, 25), parent=self,
                                    vertical=True, data_range=Time_Frame.x_range, unit="cm")

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

            for i in range(int(self.size[0] * global_values.samples_per_pixel)):
                if len(user.head_positions) == 0:
                    continue
                posindex = int(
                    len(user.head_positions) * i * (self.end - self.start) / float(
                        self.size[0] * global_values.samples_per_pixel) + self.start * len(user.head_positions))
                current_position = []
                head_position_averaged = user.get_head_position_averaged(posindex)
                head_x = (head_position_averaged[0] - database.min_x) / float(database.max_x - database.min_x)
                head_y = (head_position_averaged[1] - database.min_y) / float(database.max_y - database.min_y)
                head_z = (head_position_averaged[2] - database.min_z) / float(database.max_z - database.min_z)
                # touch_x = (user.touches[posindex][0]-database.min_touch_x)/float(database.max_touch_x-database.min_touch_x)
                # touch_y = (user.touches[posindex][1]-database.min_touch_y)/float(database.max_touch_y-database.min_touch_y)
                # touch_time = (user.touches[posindex][2]-database.min_time)/float(database.max_time-database.min_time)
                time = i / float(global_values.samples_per_pixel)

                # x value of the visualization
                current_position.append(time)
                # y value of the visualization
                current_position.append(head_x * self.size[1])

                thickness = 1+pow(head_z, 3) * 60
                opacity = (1 - head_z)
                points.append(current_position)
                widths.append(thickness)
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
                userline.set_points_and_widths(points, widths)
            else:
                self.canvasObjects.append(
                    Variable_Width_Line.Variable_Width_Line(points=points, widths=widths,  parent=self,
                                                            color=global_values.get_color_as_hex(userid, 1)))

    def draw(self):

        for user in User.users:
            for point in user.head_positions:
                None
