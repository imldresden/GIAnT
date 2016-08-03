# -*- coding: utf-8 -*-

import pat_model
import global_values
import vis_panel
import vis_params
from libavg import avg, player


class WallPanel(vis_panel.VisPanel):

    PIXELS_PER_SAMPLE = 4
    MAX_SMOOTHNESS = 500

    def __init__(self, session, vis_params, parent, **kwargs):
        super(WallPanel, self).__init__("Wall", vis_params, (60, 25), parent, **kwargs)

        self.__users = session.users

        self.__create_display_borders()
        self._create_data_div()

        self.__create_touch_bmps()
        self.__touch_nodes = []

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
        i = 0
        for user in self.__users:
            touches = user.get_touches(time_interval[0], time_interval[1])
            for touch in touches:
                if i < len(self.__touch_nodes):
                    node = self.__touch_nodes[i]
                else:
                    node = avg.ImageNode(parent=self._data_div)
                    self.__touch_nodes.append(node)
                node.pos = self.__touch_to_pixel(avg.Point2D(touch.pos))-(1,1)
                node.setBitmap(self.__touch_bmps[user.userid])
                i += 1
        num_nodes = i
        for j in range(num_nodes, len(self.__touch_nodes)):
            print num_nodes, len(self.__touch_nodes), j
            self.__touch_nodes[j].unlink(True)
        self.__touch_nodes = self.__touch_nodes[:num_nodes]

    def __touch_to_pixel(self, pos):
        touch_range = avg.Point2D(pat_model.touch_range)
        pixel_range = self._data_div.size
        return avg.Point2D(float(pos.x)/touch_range.x*pixel_range.x, float(pos.y)/touch_range.y*pixel_range.y)

    def __create_touch_bmps(self):
        self.__touch_bmps = []
        for user in self.__users:
            color = vis_params.VisParams.get_user_color(user.userid)
            canvas = player.createCanvas(id="bmpcanvas", size=(3,3))
            avg.CircleNode(pos=(1,1), r=1, strokewidth=0, fillopacity=1, fillcolor=color,
                    parent=canvas.getRootNode())
            canvas.render()
            self.__touch_bmps.append(canvas.screenshot())
            player.deleteCanvas("bmpcanvas")
