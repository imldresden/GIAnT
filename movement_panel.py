# -*- coding: utf-8 -*-

import user
import global_values
import axis
import libavg
import variable_width_line


class MovementPanel(libavg.DivNode):
    start = 0
    end = 1

    def __init__(self, parent, vis_params, **kwargs):
        super(MovementPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.crop = False

        self.canvas_objects = []

        # rect for coloured border and background
        self.background_rect = libavg.RectNode(pos=(axis.THICKNESS, 0),
                                               size=(self.width - axis.THICKNESS, self.height - axis.THICKNESS),
                                               parent=self, strokewidth=1, fillopacity=1,
                                               color=global_values.COLOR_FOREGROUND,
                                               fillcolor=global_values.COLOR_BLACK)

        # div for visualization data
        self.data_div = libavg.DivNode(pos=(axis.THICKNESS, 0),
                                       size=(self.width - axis.THICKNESS, self.height - axis.THICKNESS),
                                       parent=self, crop=True)

        # user divs to distinguish MeshNodes in data_div by user (user_divs are initialized as self.data_div's)
        self.user_divs = []
        for i in range((len(user.users))):
            self.user_divs.append(libavg.DivNode(pos=(0, 0), parent=self.data_div, crop=True, size=self.size))

        custom_label_offset = 23  # to make space for cosmetic schematic wall
        self.y_axis = axis.AxisNode(pos=(0, 0), size=(axis.THICKNESS, self.data_div.height), parent=self,
                sensitive=True, data_range=global_values.x_range, unit="cm", hide_rims=True,
                inverted=True, label_offset=custom_label_offset)

        x_axis_pos = (axis.THICKNESS, self.data_div.height)
        self.x_axis = axis.TimeAxisNode(pos=x_axis_pos, vis_params=vis_params, parent=self, unit="ms",
                data_range=vis_params.get_total_range(), size=(self.data_div.width, axis.THICKNESS), inverted=False)

        self.create_line(vis_params)

        # name
        libavg.WordsNode(pos=(axis.THICKNESS + global_values.APP_PADDING, global_values.APP_PADDING), parent=self,
                         color=global_values.COLOR_FOREGROUND, text="Movement over Time", sensitive=False, alignment="left")
        vis_params.subscribe(vis_params.CHANGED, self.update_time)

    # make start and end values in 0..1
    def update_time(self, vis_params, draw_lines):
        start_orig = self.start
        end_orig = self.end
        interval = vis_params.get_time_interval()
        total_extent = vis_params.get_total_extent()
        self.start = interval[0] / total_extent
        self.end = interval[1] / total_extent
        if draw_lines:
            self.create_line(vis_params)
        elif self.start != start_orig or self.end != end_orig:
            self.create_line(vis_params)

    def create_line(self, vis_params):
        userid = -1
        for i, usr in enumerate(user.users):
            userid += 1
            if vis_params.get_user_visible(i):
                points = []
                widths = []
                opacities = []
                samplecount = int(self.data_div.width * vis_params.get_samples_per_pixel()) + 1
                for sample in range(samplecount):
                    if len(usr.head_positions_integral) == 0:
                        continue
                    posindex = int(
                        len(usr.head_positions_integral) * sample * (self.end - self.start) / float(
                            samplecount) + self.start * len(usr.head_positions_integral))

                    head_position_averaged = usr.get_head_position_averaged(posindex, vis_params.get_smoothness())

                    norm_time = float(sample) / float(max(1, samplecount - 1))
                    norm_x = 1 - (head_position_averaged[0] - global_values.x_range[0]) / float(global_values.x_range[1] - global_values.x_range[0])
                    norm_z = (head_position_averaged[2] - global_values.z_range[0]) / float(global_values.z_range[1] - global_values.z_range[0])

                    vis_x = norm_time * self.data_div.width
                    vis_y = norm_x * self.data_div.height
                    vis_thickness = calculate_thickness(norm_z, self)
                    vis_opacity = calculate_opacity(norm_z)

                    points.append((vis_x, vis_y))
                    widths.append(vis_thickness)
                    opacities.append(vis_opacity)

                if len(self.canvas_objects) > userid:
                    userline = self.canvas_objects[userid]
                    userline.set_values(points, widths, opacities)
                else:
                    self.canvas_objects.append(
                        variable_width_line.VariableWidthLine(points=points, widths=widths, opacities=opacities,
                                                              userid=userid, parent=self.user_divs[userid]))


def calculate_thickness(data, div):
    return 1.4 + pow(data, 3) * (min(div.width, div.height)/12)


def calculate_opacity(data):
    return 0.05 + 0.95*pow((1 - data), 2)
