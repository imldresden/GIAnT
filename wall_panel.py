# -*- coding: utf-8 -*-

import pat_model
import global_values
import vis_panel
from libavg import avg


class WallPanel(vis_panel.VisPanel):

    def __init__(self, session, vis_params, parent, **kwargs):
        super(WallPanel, self).__init__("Wall", vis_params, (60, 25), False, parent, **kwargs)

        self.__users = session.users

        pos_range = pat_model.pos_range
        self._create_x_axis(data_range=(pos_range[0][0], pos_range[1][0]), unit="m")
        self._create_y_axis(data_range=(pos_range[0][1], pos_range[1][1]), unit="m", hide_rims=True, inverted=True)

        # Calculate size of wall in pixels.
        view_extent = (pos_range[1][0] - pos_range[0][0], pos_range[1][1] - pos_range[0][1])
        normalized_wall_pos = avg.Point2D((pat_model.x_wall_range[0] - pos_range[0][0]) / view_extent[0],
                (pat_model.y_wall_range[1] - pos_range[0][1]) / view_extent[1])
        wall_pos = avg.Point2D(self._data_div.size.x * normalized_wall_pos.x,
                self._data_div.size.y * (1-normalized_wall_pos.y))
        wall_size = avg.Point2D(self._data_div.size.x * pat_model.x_wall_range[1] / view_extent[0],
                self._data_div.size.y * (1-pat_model.y_wall_range[0] / view_extent[1]))
        avg.RectNode(pos=wall_pos, size=wall_size, color=global_values.COLOR_SECONDARY,
                parent=self._data_div)

        self.__plot_div = avg.DivNode(pos=wall_pos, size=wall_size, parent=self._data_div)
        self._create_data_div()
        self.__create_display_borders()

        self.__plot_nodes = []
        for user in self.__users:
            color = vis_params.get_user_color(user.userid)
            node = plots.ScatterPlotNode(size=self.__plot_div.size, viewportrangemax=pat_model.touch_range,
                    color=color, parent=self.__plot_div)
            self.__plot_nodes.append(node)

    def _update_time(self, vis_params):
        self.__show_touches(vis_params.get_time_interval())

    def __create_display_borders(self):
        parent = self.__plot_div
        for i in range(1,3):
            y = i/3. * parent.height
            avg.LineNode(pos1=(0, y), pos2=(parent.width, y), color=global_values.COLOR_BACKGROUND,
                    parent=parent)

        for i in range(1, 4):
            x = i / 4. * parent.width
            avg.LineNode(pos1=(x, 0), pos2=(x, parent.height), color=global_values.COLOR_BACKGROUND,
                parent=parent)

    def __show_touches(self, time_interval):
        for i, user in enumerate(self.__users):
            touches = user.get_touches(time_interval[0], time_interval[1])
            touch_posns = [touch.pos for touch in touches]
            self.__plot_nodes[i].setPosns(touch_posns)
