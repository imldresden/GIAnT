import libavg
import Line_Visualization
import Variable_Width_Line
import global_values


class Legend(libavg.DivNode):
    def __init__(self, parent, min_value, max_value, unit, **kwargs):
        super(Legend, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        v_center = self.height/2 + 5
        libavg.LineNode(pos1=(10, v_center), pos2=(10, self.height - 10), color="FFFFFF", parent=self)
        libavg.LineNode(pos1=(self.width - 10, v_center), pos2=(self.width - 10, self.height - 10), color="FFFFFF", parent=self)
        libavg.LineNode(pos1=(10, self.height - 10), pos2=(self.width - 10, self.height - 10), parent=self, color="FFFFFF")

        points = []
        widths = []
        opacities = []
        for i in range(0, 101):
            value = i / 100.0
            points.append((10 + (self.width - 20) * value, v_center))
            widths.append(Line_Visualization.calculate_thickness(value, parent.getParent().main_visualization.data_div))
            opacities.append(Line_Visualization.calculate_opacity(value))
        Variable_Width_Line.Variable_Width_Line(points, widths, opacities, -1, self)
        libavg.WordsNode(pos=(10, 0), text="Distance from wall", parent=self, color="FFFFFF")
        libavg.WordsNode(pos=(0, self.height/2), text=str(round(global_values.z_range[0], 1)) + unit, parent=self, color="FFFFFF", alignment="right")
        libavg.WordsNode(pos=(self.width, self.height/2), text=str(round(global_values.z_range[1], 1)) + unit, parent=self, color="FFFFFF", alignment="left")
