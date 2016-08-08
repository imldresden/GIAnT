# -*- coding: utf-8 -*-

import pat_model
import global_values
import vis_panel
from libavg import avg, player

player.loadPlugin("heatmap")

class WallPanel(vis_panel.VisPanel):

    def __init__(self, session, vis_params, parent, **kwargs):
        pos_range = pat_model.pos_range
        view_extent = avg.Point2D(pos_range[1][0] - pos_range[0][0], pos_range[1][1] - pos_range[0][1])
        aspect = view_extent.y/view_extent.x
        super(WallPanel, self).__init__("Wall", vis_params, (60, 25), False, aspect, parent, **kwargs)

        self.__users = session.users

        self._create_x_axis(data_range=(pos_range[0][0], pos_range[1][0]), unit="m")
        self._create_y_axis(data_range=(pos_range[0][1], pos_range[1][1]), unit="m", hide_rims=True, inverted=True)

        # Calculate size of wall in pixels.
        normalized_wall_pos = avg.Point2D((pat_model.x_wall_range[0] - pos_range[0][0]) / view_extent.x,
                (pat_model.y_wall_range[1] - pos_range[0][1]) / view_extent.y)
        wall_pos = avg.Point2D(self._data_div.size.x * normalized_wall_pos.x,
                self._data_div.size.y * (1-normalized_wall_pos.y))
        wall_size = avg.Point2D(self._data_div.size.x * pat_model.x_wall_range[1] / view_extent.x,
                self._data_div.size.y * (1-pat_model.y_wall_range[0] / view_extent.y))
        avg.RectNode(pos=wall_pos, size=wall_size, color=global_values.COLOR_SECONDARY,
                parent=self._data_div)

        self.__plot_div = avg.DivNode(pos=wall_pos, size=wall_size, parent=self._data_div)
        self._create_data_div()
        self.__create_display_borders()

        self.__plot_nodes = []
        self.__heatmap_nodes = []
        for user in self.__users:
            color = vis_params.get_user_color(user.userid)

            color_map, opacity_map = self.__create_color_map("000000", color, 16)
            node = heatmap.HeatMapNode(size=self.__plot_div.size,
                    viewportrangemin=(pat_model.x_wall_range[0], pat_model.y_wall_range[0]),
                    viewportrangemax=(pat_model.x_wall_range[1], pat_model.y_wall_range[1]),
                    mapsize=(32,16), valuerangemin=0, valuerangemax=16,
                    colormap=color_map, opacitymap=opacity_map, blendmode="add", parent=self.__plot_div)
            self.__heatmap_nodes.append(node)

            node = plots.ScatterPlotNode(size=self.__plot_div.size, viewportrangemax=pat_model.touch_range,
                    color=color, parent=self.__plot_div)
            self.__plot_nodes.append(node)

    def _update_time(self, vis_params):
        self.__show_touches(vis_params.get_time_interval())
        self.__show_viewpoints(vis_params.get_time_interval())

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

    def __show_viewpoints(self, time_interval):
        for i, user in enumerate(self.__users):
            viewpoints = user.get_viewpoints(time_interval)
            self.__heatmap_nodes[i].setPosns(viewpoints)

    def __create_color_map(self, start_color, end_color, steps):
        color_map = []
        opacity_map = []
        for i in xrange(steps):
            color = avg.Color.mix(end_color, start_color, float(i)/steps)
            color_map.append(str(color))
            opacity_map.append(float(i)/steps)
        return color_map, opacity_map

