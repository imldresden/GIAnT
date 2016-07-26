# -*- coding: utf-8 -*-

import pat_model
import global_values
import axis
from libavg import avg
from libavg import player
import util

player.loadPlugin("vwline")


class MovementPanel(avg.DivNode):

    PIXELS_PER_SAMPLE = 4

    def __init__(self, parent, users, vis_params, **kwargs):
        super(MovementPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.crop = False

        self.__time_min = pat_model.time_range[0]
        self.__time_max = pat_model.time_range[1]

        # rect for coloured border and background
        self.background_rect = avg.RectNode(pos=(axis.THICKNESS, 0),
                                               size=(self.width - axis.THICKNESS, self.height - axis.THICKNESS),
                                               parent=self, strokewidth=1, fillopacity=1,
                                               color=global_values.COLOR_FOREGROUND,
                                               fillcolor=global_values.COLOR_BLACK)

        # div for visualization data
        self.data_div = avg.DivNode(pos=(axis.THICKNESS, 0),
                                       size=(self.width - axis.THICKNESS, self.height - axis.THICKNESS),
                                       crop=True)
        self.__users = users
        self.__user_lines = []
        self.__touch_nodes = []
        max_width = (min(self.width, self.height) / 12)
        for userid in range(len(users)):
            color = util.get_user_color_as_hex(userid, 1)
            self.__user_lines.append(vwline.VWLineNode(color=color, maxwidth=max_width, parent=self.data_div))

        custom_label_offset = 23  # to make space for cosmetic schematic wall
        x_range = pat_model.pos_range[0][0], pat_model.pos_range[1][0]
        self.y_axis = axis.AxisNode(pos=(0, 0), size=(axis.THICKNESS, self.data_div.height), parent=self,
                sensitive=True, data_range=x_range, unit="cm", hide_rims=True,
                inverted=True, label_offset=custom_label_offset)

        x_axis_pos = (axis.THICKNESS, self.data_div.height)
        self.x_axis = axis.TimeAxisNode(pos=x_axis_pos, vis_params=vis_params, parent=self, unit="ms",
                data_range=pat_model.time_range, size=(self.data_div.width, axis.THICKNESS), inverted=False)

        self.appendChild(self.data_div)

        self.__create_line(vis_params)

        self.__highlight_line = avg.LineNode(color=global_values.COLOR_SECONDARY,
                pos1=(0, 0), pos2=(0, self.data_div.height), opacity=1, parent=self.data_div)
        self.__hover_id = self.data_div.subscribe(avg.Node.CURSOR_MOTION, self.__on_hover)

        # name
        avg.WordsNode(pos=(axis.THICKNESS + global_values.APP_PADDING, global_values.APP_PADDING), parent=self,
                         color=global_values.COLOR_FOREGROUND, text="Movement over Time", sensitive=False, alignment="left")

        vis_params.subscribe(vis_params.CHANGED, self.update_time)
        self.__vis_params = vis_params
        self.data_div.subscribe(avg.Node.MOUSE_WHEEL, self.__on_mouse_wheel)

    def update_time(self, vis_params, draw_lines):
        min_orig = self.__time_min
        max_orig = self.__time_max
        interval = vis_params.get_time_interval()
        self.__time_min = interval[0]
        self.__time_max = interval[1]
        if draw_lines:
            self.__create_line(vis_params)
        elif self.__time_min != min_orig or self.__time_max != max_orig:
            self.__create_line(vis_params)

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

    def __create_line(self, vis_params):
        time_start = self.__xpos_to_time(0)
        time_end = self.__xpos_to_time(self.data_div.width)
        for i, user in enumerate(self.__users):
            if vis_params.get_user_visible(i):
                points = []
                dists = []
                for cur_sample_x in range(0, int(self.data_div.width), self.PIXELS_PER_SAMPLE):
                    cur_time = self.__xpos_to_time(cur_sample_x)

                    head_position_averaged = user.get_head_position_averaged(cur_time, vis_params.get_smoothness())

                    pos_range = pat_model.pos_range
                    norm_x = 1 - (head_position_averaged[0] - pos_range[0][0]) / float(pos_range[1][0] - pos_range[0][0])
                    norm_z = (head_position_averaged[2] - pos_range[0][2]) / float(pos_range[1][2] - pos_range[0][2])

                    vis_y = norm_x * self.data_div.height

                    points.append(avg.Point2D(cur_sample_x, vis_y))
                    dists.append(norm_z)

                userline = self.__user_lines[i]
                userline.setValues(points, dists)
                touches = user.get_touches(time_start, time_end)
                touches_x = [self.__time_to_xpos(touch.time) for touch in touches]
                userline.setHighlights(touches_x)

    def __on_hover(self, event=None):
        """
        Moves the highlight line along the vertical mouse position.
        """
        rel_pos = self.data_div.getRelPos(event.pos)
        self.__vis_params.highlight_time = self.x_axis.calculate_time_from_pixel(rel_pos.x)
        self.__vis_params.notify(False)

    def __xpos_to_time(self, x):
        norm_time = x / self.data_div.width
        return norm_time * (self.__time_max - self.__time_min) + self.__time_min

    def __time_to_xpos(self, t):
        norm_time = (float(t)-self.__time_min) / (self.__time_max-self.__time_min)
        return norm_time * self.data_div.width
