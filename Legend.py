# -*- coding: utf-8 -*-

import libavg
import movement_panel
import variable_width_line
import global_values


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
            points.append((self.width * value, self.height))
            widths.append(movement_panel.calculate_thickness(value,
                                                                 parent.getParent().main_visualization.data_div) * 2)
            opacities.append(movement_panel.calculate_opacity(value))

        var_line_div = libavg.DivNode(pos=(0, 0), size=(self.width, self.height), crop=True, parent=self)
        variable_width_line.VariableWidthLine(points, widths, opacities, -1, var_line_div)

        # texts
        libavg.WordsNode(pos=(0, self.height - 35), text="Distance from wall", parent=self,
                         color=global_values.COLOR_FOREGROUND)
        libavg.WordsNode(pos=(0, self.height - 20), text="{} {}".format(str(int(global_values.z_range[0])), unit),
                         parent=self, color=global_values.COLOR_FOREGROUND, alignment="right")
        libavg.WordsNode(pos=(self.width + 2, self.height - 20), parent=self, alignment="left",
                         text="{} {}".format(str(int(global_values.z_range[1])), unit),
                         color=global_values.COLOR_FOREGROUND, )
