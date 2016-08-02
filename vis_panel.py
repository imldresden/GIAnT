# -*- coding: utf-8 -*-

import pat_model
import axis
import global_values
from libavg import avg, player

class VisPanel(avg.DivNode):

    def __init__(self, label, session, vis_params, axis_size, parent, **kwargs):
        super(VisPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.__axis_size = avg.Point2D(axis_size)

        # rect for coloured border and background
        avg.RectNode(pos=(self.__axis_size.x, 0), size=self.size - self.__axis_size,
                strokewidth=1, fillopacity=1,
                color=global_values.COLOR_FOREGROUND, fillcolor=global_values.COLOR_BLACK,
                parent=self)

        self._data_div = avg.DivNode(pos=(self.__axis_size.x, 0), size=self.size - self.__axis_size, crop=True)

        avg.WordsNode(pos=(10, 10), color=global_values.COLOR_FOREGROUND, text=label, sensitive=False,
            parent=self._data_div)

    def _create_x_axis(self, data_range, unit, hide_rims=False, top_axis=False, inverted=False):
        pos = (self.__axis_size.x, self._data_div.height)
        self._x_axis = axis.AxisNode(pos=pos, size=(self._data_div.width, self.__axis_size.y),
                panel_height=self._data_div.height, unit=unit, data_range=data_range,
                hide_rims=hide_rims, top_axis=top_axis, inverted=inverted, parent=self)

    def _create_y_axis(self, data_range, unit, hide_rims=False, label_offset=0, inverted=False):
        self.y_axis = axis.AxisNode(pos=(0, 0), size=(self.__axis_size.x, self._data_div.height),
                panel_height=self._data_div.height, data_range=data_range, unit=unit,
                hide_rims=hide_rims, inverted=inverted, label_offset=label_offset,
                parent=self)

    def _create_data_div(self):
        self.appendChild(self._data_div)
