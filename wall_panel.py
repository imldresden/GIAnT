# -*- coding: utf-8 -*-

import pat_model
import global_values
import vis_panel
from libavg import avg


class WallPanel(vis_panel.VisPanel):

    PIXELS_PER_SAMPLE = 4
    MAX_SMOOTHNESS = 500

    def __init__(self, session, vis_params, parent, **kwargs):
        super(WallPanel, self).__init__("Wall", vis_params, (60, 25), parent, **kwargs)

        self.__users = session.users

        self.__create_display_borders()
        self._create_data_div()

        self.__plot_nodes = []
        for user in self.__users:
            color = vis_params.get_user_color(user.userid)
            node = plots.ScatterPlotNode(size=self._data_div.size, viewportrangemax=pat_model.touch_range,
                    color=color, parent=self._data_div)
            self.__plot_nodes.append(node)

    def _update_time(self, vis_params):
        self.__show_touches(vis_params.get_time_interval())

    def __create_display_borders(self):
        for i in range(1,3):
            y = i/3. * self._grid_div.height
            avg.LineNode(pos1=(0,y), pos2=(self._grid_div.width,y), color=global_values.COLOR_BACKGROUND,
                    parent=self._grid_div)

        for i in range(1, 4):
            x = i / 4. * self._grid_div.width
            avg.LineNode(pos1=(x, 0), pos2=(x, self._grid_div.height), color=global_values.COLOR_BACKGROUND,
                parent=self._grid_div)

    def __show_touches(self, time_interval):
        for i, user in enumerate(self.__users):
            touches = user.get_touches(time_interval[0], time_interval[1])
            touch_posns = [touch.pos for touch in touches]
            self.__plot_nodes[i].setPosns(touch_posns)
