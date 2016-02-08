import libavg
import Line_Visualization
import Variable_Width_Line
import global_values


class Legend(libavg.DivNode):
    def __init__(self, parent, min_value, max_value, unit, **kwargs):
        super(Legend, self).__init__(**kwargs)
        self.registerInstance(self, parent)
<<<<<<< HEAD
        v_center = self.height / 2 + 5
=======
>>>>>>> origin/master

        points = []
        widths = []
        opacities = []
        for i in range(0, 101):
            value = i / 100.0
            points.append((self.width * value, self.height))
            widths.append(Line_Visualization.calculate_thickness(value, parent.getParent().main_visualization.data_div)*2)
            opacities.append(Line_Visualization.calculate_opacity(value))
        var_line_div = libavg.DivNode(pos=(0,0), size=(self.width, self.height), crop=True, parent=self)
        Variable_Width_Line.Variable_Width_Line(points, widths, opacities, -1, var_line_div)
        libavg.WordsNode(pos=(0, self.height - 35), text="Distance from wall", parent=self, color=global_values.COLOR_FOREGROUND)
        libavg.WordsNode(pos=(0, self.height - 20), text="{} {}".format(str(int(global_values.z_range[0])), unit), parent=self, color=global_values.COLOR_FOREGROUND, alignment="right")
        libavg.WordsNode(pos=(self.width + 2, self.height - 20), text="{} {}".format(str(int(global_values.z_range[1])), unit), parent=self, color=global_values.COLOR_FOREGROUND, alignment="left")
