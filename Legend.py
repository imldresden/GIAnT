# -*- coding: utf-8 -*-

import libavg
from libavg import player
import global_values
import pat_model
import util

player.loadPlugin("vwline")


class Legend(libavg.DivNode):
    def __init__(self, parent, min_value, max_value, unit, **kwargs):
        super(Legend, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.sensitive = False

        points = []
        dists = []

        for i in range(0, 101):
            value = i / 100.0
            points.append(libavg.Point2D(self.width * value, self.height))
            dists.append(value)

        data_div = parent.getParent().main_visualization.data_div
        var_line_div = libavg.DivNode(pos=(0, 0), size=(self.width, self.height), crop=True, parent=self)
        max_width = (min(data_div.width, data_div.height) / 12)
        line = vwline.VWLineNode(color=util.get_user_color_as_hex(-1, 1), maxwidth=max_width, parent=var_line_div)
        line.setValues(points, dists)

        # texts
        libavg.WordsNode(pos=(0, self.height - 35), text="Distance from wall", parent=self,
                         color=global_values.COLOR_FOREGROUND)
        pos_range = pat_model.pos_range
        libavg.WordsNode(pos=(0, self.height - 20), text="{} {}".format(str(int(pos_range[0][2])), unit),
                         parent=self, color=global_values.COLOR_FOREGROUND, alignment="right")
        libavg.WordsNode(pos=(self.width + 2, self.height - 20), parent=self, alignment="left",
                         text="{} {}".format(str(int(pos_range[1][2])), unit),
                         color=global_values.COLOR_FOREGROUND, )
