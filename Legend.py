# -*- coding: utf-8 -*-

import libavg
from libavg import player
import movement_panel
import global_values
import util

player.loadPlugin("vwline")


class Legend(libavg.DivNode):
    def __init__(self, parent, min_value, max_value, unit, **kwargs):
        super(Legend, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.sensitive = False

        points = []
        widths = []
        opacities = []

        for i in range(0, 101):
            value = i / 100.0
            points.append(libavg.Point2D(self.width * value, self.height))
            widths.append(movement_panel.calculate_thickness(value,
                                                                 parent.getParent().main_visualization.data_div) * 2)
            opacities.append(movement_panel.calculate_opacity(value))

        var_line_div = libavg.DivNode(pos=(0, 0), size=(self.width, self.height), crop=True, parent=self)
        line = vwline.VWLineNode(color=util.get_user_color_as_hex(-1, 1), parent=var_line_div)
        line.setValues(points, widths, opacities)

        # texts
        libavg.WordsNode(pos=(0, self.height - 35), text="Distance from wall", parent=self,
                         color=global_values.COLOR_FOREGROUND)
        libavg.WordsNode(pos=(0, self.height - 20), text="{} {}".format(str(int(global_values.z_range[0])), unit),
                         parent=self, color=global_values.COLOR_FOREGROUND, alignment="right")
        libavg.WordsNode(pos=(self.width + 2, self.height - 20), parent=self, alignment="left",
                         text="{} {}".format(str(int(global_values.z_range[1])), unit),
                         color=global_values.COLOR_FOREGROUND, )
