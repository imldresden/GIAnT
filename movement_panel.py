# -*- coding: utf-8 -*-

import user
import global_values
import axis
import libavg
from libavg import player
import util

player.loadPlugin("vwline")


class MovementPanel(libavg.DivNode):
    start = 0
    end = 1

    PIXELS_PER_SAMPLE = 4

    def __init__(self, parent, vis_params, **kwargs):
        super(MovementPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.crop = False

        # rect for coloured border and background
        self.background_rect = libavg.RectNode(pos=(axis.THICKNESS, 0),
                                               size=(self.width - axis.THICKNESS, self.height - axis.THICKNESS),
                                               parent=self, strokewidth=1, fillopacity=1,
                                               color=global_values.COLOR_FOREGROUND,
                                               fillcolor=global_values.COLOR_BLACK)

        # div for visualization data
        self.data_div = libavg.DivNode(pos=(axis.THICKNESS, 0),
                                       size=(self.width - axis.THICKNESS, self.height - axis.THICKNESS),
                                       crop=True)
        self.__user_lines = []
        max_width = (min(self.width, self.height) / 12)
        for userid in range(len(user.users)):
            color = util.get_user_color_as_hex(userid, 1)
            self.__user_lines.append(vwline.VWLineNode(color=color, maxwidth=max_width, parent=self.data_div))

        custom_label_offset = 23  # to make space for cosmetic schematic wall
        x_range = global_values.pos_range[0][0], global_values.pos_range[1][0]
        self.y_axis = axis.AxisNode(pos=(0, 0), size=(axis.THICKNESS, self.data_div.height), parent=self,
                sensitive=True, data_range=x_range, unit="cm", hide_rims=True,
                inverted=True, label_offset=custom_label_offset)

        x_axis_pos = (axis.THICKNESS, self.data_div.height)
        self.x_axis = axis.TimeAxisNode(pos=x_axis_pos, vis_params=vis_params, parent=self, unit="ms",
                data_range=global_values.time_range, size=(self.data_div.width, axis.THICKNESS), inverted=False)

        self.appendChild(self.data_div)

        self.create_line(vis_params)

        self.__highlight_line = libavg.LineNode(color=global_values.COLOR_SECONDARY,
                pos1=(0, 0), pos2=(0, self.data_div.height), opacity=1, parent=self.data_div)
        self.__hover_id = self.data_div.subscribe(libavg.Node.CURSOR_MOTION, self.__on_hover)

        # name
        libavg.WordsNode(pos=(axis.THICKNESS + global_values.APP_PADDING, global_values.APP_PADDING), parent=self,
                         color=global_values.COLOR_FOREGROUND, text="Movement over Time", sensitive=False, alignment="left")

        vis_params.subscribe(vis_params.CHANGED, self.update_time)
        self.__vis_params = vis_params
        self.data_div.subscribe(libavg.Node.MOUSE_WHEEL, self.__on_mouse_wheel)

    # make start and end values in 0..1
    def update_time(self, vis_params, draw_lines):
        start_orig = self.start
        end_orig = self.end
        interval = vis_params.get_time_interval()
        time_extent = global_values.time_range[1] - global_values.time_range[0]
        self.start = interval[0] / time_extent
        self.end = interval[1] / time_extent
        if draw_lines:
            self.create_line(vis_params)
        elif self.start != start_orig or self.end != end_orig:
            self.create_line(vis_params)

        # update position of pinned highlight line and highlight line marker
        highlight_xpos = self.__time_to_xpos(self.__vis_params.highlight_time)
        if highlight_xpos > self.width or highlight_xpos < 0:
            self.__highlight_line.opacity = 0
        else:
            self.__highlight_line.opacity = 1
            self.__highlight_line.pos1 = (highlight_xpos, self.__highlight_line.pos1[1])
            self.__highlight_line.pos2 = (highlight_xpos, self.__highlight_line.pos2[1])

        for i, user_line in enumerate(self.__user_lines):
            user_line.active = vis_params.get_user_visible(i)

    def __on_mouse_wheel(self, event):
        rel_pos = self.data_div.getRelPos(event.pos)
        pos_fraction = rel_pos[0]/self.data_div.width
        if event.motion.y > 0:
            self.__vis_params.zoom_in_at(pos_fraction)
        else:
            self.__vis_params.zoom_out_at(pos_fraction)

    def create_line(self, vis_params):
        userid = -1
        for i, usr in enumerate(user.users):
            userid += 1
            if vis_params.get_user_visible(i):
                points = []
                dists = []
                num_head_positions = len(usr.head_positions_integral)
                for cur_sample_x in range(0, int(self.data_div.width), self.PIXELS_PER_SAMPLE):
                    posindex = int(
                        num_head_positions * (cur_sample_x * (self.end - self.start) / float(self.data_div.width)
                                              + self.start))

                    head_position_averaged = usr.get_head_position_averaged(posindex, vis_params.get_smoothness())

                    pos_range = global_values.pos_range
                    norm_x = 1 - (head_position_averaged[0] - pos_range[0][0]) / float(pos_range[1][0] - pos_range[0][0])
                    norm_z = (head_position_averaged[2] - pos_range[0][2]) / float(pos_range[1][2] - pos_range[0][2])

                    vis_y = norm_x * self.data_div.height

                    points.append(libavg.Point2D(cur_sample_x, vis_y))
                    dists.append(norm_z)

                userline = self.__user_lines[userid]
                userline.setValues(points, dists)

    def __on_hover(self, event=None):
        """
        Moves the highlight line along the vertical mouse position.
        """
        rel_pos = self.data_div.getRelPos(event.pos)
        self.__vis_params.highlight_time = self.x_axis.calculate_time_from_pixel(rel_pos.x)
        self.__vis_params.notify(False)

    def __time_to_xpos(self, t):
        (start, end) = self.__vis_params.get_time_interval()
        norm_time = (float(t)-start) / (end-start)
        return norm_time * self.data_div.width
