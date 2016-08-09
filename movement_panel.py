# -*- coding: utf-8 -*-

import math

import pat_model
import global_values
import vis_panel
from libavg import avg, player

player.loadPlugin("plots")


class MovementPanel(vis_panel.VisPanel):

    PIXELS_PER_SAMPLE = 4
    MAX_SMOOTHNESS = 500

    def __init__(self, session, vis_params, parent, **kwargs):
        super(MovementPanel, self).__init__("Timeline", vis_params, (60, 25), True, parent=parent, **kwargs)

        self.__duration = session.duration
        self.__users = session.users

        self.__user_lines = []
        max_width = (min(self.width, self.height) / 12)
        for userid in range(session.num_users):
            color = vis_params.get_user_color(userid)
            self.__user_lines.append(plots.VWLineNode(color=color, maxwidth=max_width,
                    blendmode="add", parent=self._data_div))

        x_range = pat_model.pos_range[0][0], pat_model.pos_range[1][0]
        self._create_y_axis(data_range=x_range, unit="m", hide_rims=True, label_offset=15, inverted=True)
        self._create_x_axis(data_range=[0, session.duration], unit="s")
        self.__create_wall_rect()
        self._create_data_div()

        self.__time_factor = self._data_div.width / vis_params.get_time_duration()

        self.__highlight_line = avg.LineNode(color=global_values.COLOR_SECONDARY,
                pos1=(0, 0), pos2=(0, self._data_div.height), opacity=1, parent=self._data_div)
        self.__hover_id = self._data_div.subscribe(avg.Node.CURSOR_MOTION, self.__on_hover)

#        self.legend = Legend(size=(250, 100), maxwidth=max_width, color=vis_params.get_user_color(-1), parent=self)
#        self.legend.pos = (self.width - self.legend.width - 10, 10)

        self.__enable_time = True
        vis_params.subscribe(vis_params.IS_PLAYING, self.__on_play_pause)

        self._data_div.subscribe(avg.Node.MOUSE_WHEEL, self.__on_mouse_wheel)

    def _update_time(self, vis_params):
        interval = vis_params.get_time_interval()
        self.__time_min = interval[0]
        self.__time_factor = self._data_div.width / vis_params.get_time_duration()
        self.__create_lines(vis_params)
        # update position of pinned highlight line and highlight line marker
        highlight_xpos = self.__time_to_xpos(self._vis_params.highlight_time)
        if highlight_xpos > self.width or highlight_xpos < 0:
            self.__highlight_line.opacity = 0
        else:
            self.__highlight_line.opacity = 1
            self.__highlight_line.pos1 = (highlight_xpos, self.__highlight_line.pos1[1])
            self.__highlight_line.pos2 = (highlight_xpos, self.__highlight_line.pos2[1])

        for i, user_line in enumerate(self.__user_lines):
            user_line.active = vis_params.get_user_visible(i)

        self._x_axis.hide_rims = not(math.fabs(vis_params.get_time_duration() - self.__duration) < 0.0001)
        self._x_axis.update(interval[0], interval[1])
        self._update_grid()

    def __on_play_pause(self, playing):
        self.__enable_time = not playing

    def __on_mouse_wheel(self, event):
        if self.__enable_time:
            rel_pos = self._data_div.getRelPos(event.pos)
            pos_fraction = rel_pos[0]/self._data_div.width
            if event.motion.y > 0:
                self._vis_params.zoom_in_at(pos_fraction)
            else:
                self._vis_params.zoom_out_at(pos_fraction)

    def __create_lines(self, vis_params):
        time_start = self.__xpos_to_time(0)
        time_end = self.__xpos_to_time(self._data_div.width)
        smoothness = self.__calc_smoothness(vis_params.get_smoothness_factor(), time_end-time_start)

        pos_range = pat_model.pos_range
        x_extent = float(pos_range[1][0] - pos_range[0][0])
        y_extent = float(pos_range[1][2] - pos_range[0][2])
        vis_height = self._data_div.height
        for i, user in enumerate(self.__users):
            if vis_params.get_user_visible(i):
                points = []
                dists = []
                for cur_sample_x in range(0, int(self._data_div.width), self.PIXELS_PER_SAMPLE):
                    cur_time = self.__xpos_to_time(cur_sample_x)

                    head_position_averaged = user.get_head_position_averaged(cur_time, smoothness)

                    norm_x = 1 - (head_position_averaged[0] - pos_range[0][0]) / x_extent
                    norm_z = (head_position_averaged[2] - pos_range[0][2]) / y_extent

                    vis_y = norm_x * vis_height

                    points.append((cur_sample_x, vis_y))
                    dists.append(norm_z)

                userline = self.__user_lines[i]
                userline.setValues(points, dists)
                touches = user.get_touches((time_start, time_end))
                touches_x = [self.__time_to_xpos(touch.timestamp) for touch in touches]
                touches_width = [touch.duration*self.__time_factor for touch in touches]
                userline.setHighlights(touches_x, touches_width)

    def __create_wall_rect(self):
        y_min = self._y_axis.value_to_pixel(0)
        y_max = self._y_axis.value_to_pixel(pat_model.wall_width)

        avg.RectNode(pos=(40, y_min), size=(16, y_max-y_min), fillcolor=global_values.COLOR_DARK_GREY,
                fillopacity=1, parent=self)

    def __on_hover(self, event=None):
        """
        Moves the highlight line along the vertical mouse position.
        """
        if self.__enable_time:
            rel_pos = self._data_div.getRelPos(event.pos)
            self._vis_params.highlight_time = self.__xpos_to_time(rel_pos.x)
            self._vis_params.notify()

    def __xpos_to_time(self, x):
        return x / self.__time_factor + self._vis_params.get_time_interval()[0]

    def __time_to_xpos(self, t):
        return (float(t)-self._vis_params.get_time_interval()[0]) * self.__time_factor

    def __calc_smoothness(self, smoothness_factor, time_range):
        smoothness = int((time_range / self._vis_params.get_time_interval()[1]) * self.MAX_SMOOTHNESS * smoothness_factor)
        if smoothness < 1:
            smoothness = 1
        return smoothness


class Legend(avg.DivNode):
    def __init__(self, color, maxwidth, parent, **kwargs):
        super(Legend, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.sensitive = False

        # Background
        avg.RectNode(size=self.size, color=global_values.COLOR_FOREGROUND, fillopacity=1,
                fillcolor=global_values.COLOR_BLACK, parent=self)

        points = []
        dists = []

        line_div = avg.DivNode(pos=(20,10), size=self.size - (40, 20), parent=self)

        line = plots.VWLineNode(color=color, maxwidth=maxwidth, parent=line_div)
        for i in range(0, 101):
            value = i / 100.0
            points.append(libavg.Point2D(line_div.width * value, line_div.height/2))
            dists.append(value)

        line.setValues(points, dists)

        # texts
        libavg.WordsNode(pos=(5,5), text="Distance from wall", parent=self,
                         color=global_values.COLOR_FOREGROUND)
        pos_range = pat_model.pos_range
        self.__create_label(pos=(30, self.height - 25), val=pos_range[0][2])
        self.__create_label(pos=(self.width -30, self.height - 25), val=pos_range[1][2])

    def __create_label(self, pos, val):
        val_str = "{:1.2f}m".format(val)
        libavg.WordsNode(pos=pos, text=val_str, color=global_values.COLOR_FOREGROUND, alignment="center", parent=self)
