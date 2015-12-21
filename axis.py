# -*- coding: utf-8 -*-

import libavg
import database
import Util
from libavg import avg


class AxisNode(avg.DivNode):
    """
    Custom AxisNode with axis lines and labeling. Vertical if horizontal=False
    """

    __div_size = avg.DivNode.size       # size of AxisNode

    def __init__(self, vertical=False, parent=None, **kwargs):
        super(AxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        """
        attributes
        """
        self.__x_pos = self.width / 2   # default vertical positioning of main axis line inside AxisNode area
        self.__y_pos = self.height / 2  # default horizontal positioning of main axis line inside AxisNode area
        self.__label_values = []        # contains the data values of the tick labels of the axis
        self._label_pos = []            # contains the position along the axis for each label in __label_values
        self._ticks = []                # separation lines (ticks) for axis
        self._labels = []               # nice numbers for tick labels from __label_values
        self._label_nodes = []         # contains WordNodes for tick labels with text values from _labels

        # temp rect to visualize div area
        self.rect = avg.RectNode(size=self.size, fillopacity=.1, fillcolor="FFFFFF", color="000000", parent=self)

        # create horizontal or vertical main axis line
        if vertical:
            self.size = (self.size[1], self.size[0])
            libavg.LineNode(strokewidth=1, pos1=(self.__x_pos, self.height), pos2=(self.__x_pos, 0), parent=self)
        else:
            libavg.LineNode(strokewidth=1, pos1=(0, self.__y_pos), pos2=(self.width, self.__y_pos), parent=self)

        self.update(database.min_time, database.max_time)

    def _draw_ticks(self):
        # delete old axis ticks
        for tick in self._ticks:
            tick.unlink()
        self._ticks = [None] * len(self._label_pos)

        # delete old axis labels
        for label in self._label_nodes:
            label.unlink()
        self._label_nodes = [None] * len(self._label_pos)

        for i, pos in enumerate(self._label_pos):
            if type(self._ticks[i]) is not "libavg.avg.LineNode":
                # create new axis tick and label at pos
                self._ticks[i] = libavg.LineNode(strokewidth=1, parent=self)
                self._label_nodes[i] = libavg.WordsNode(color="FFFFFF", parent=self)

            # set position of tick and label on axis
            self._ticks[i].pos1 = (pos, 10)
            self._ticks[i].pos2 = (pos, 30)
            self._label_nodes[i].pos = (pos - 10, 20)

            # set label value
            self._label_nodes[i].text = "{}".format(self._labels[i])

    def update(self, start, end):
        self.__label_values = Util.r_pretty(dmin=start, dmax=end, n=5)
        self._label_pos = [self._value_to_pixel(t, start, end) for t in self.__label_values]
        self._labels = [self._format_label_value(v) for v in self.__label_values]
        self._draw_ticks()

    def _format_label_value(self, v):
        # cut zeros if value is integer
        if v % 1 in (0, 0.0):
            v = int(v)
        # add SI prefix for one million
        if v >= 1000000:
            v = "{}M".format(v / 1000000)
        # add SI prefix for one thousand
        elif v >= 1000:
            v = "{}k".format(v / 1000)


        return v

    def _value_to_pixel(self, value, start, end):
        return value / ((end - start) / self.width)

    """
    properties
    """
    def __getSize(self):
        return self.__div_size

    def __setSize(self, size):
        self.rect.size = size
        self.__div_size = size
        self.__x_pos = size[0] / 2
        self.__y_pos = size[1] / 2

    def __get_x_pos(self):
        return self.__x_pos

    def __set_x_pos(self, x):
        self.__x_pos = x

    def __get_y_pos(self):
        return self.__y_pos

    def __set_y_pos(self, y):
        self.__y_pos = y

    def __get_label_values(self):
        return self.__label_values

    def __set_label_values(self, values):
        self.__label_values = values

    size = property(__getSize, __setSize)
    x_pos = property(__get_x_pos, __set_x_pos)
    y_pos = property(__get_y_pos, __set_y_pos)
    label_values = property(__get_label_values, __set_label_values)


class TimeAxisNode(AxisNode):

    # time values
    start_time = 45
    end_time = 134

    def __init__(self, parent=None, **kwargs):
        # pass arguments to super and initialize C++ class
        super(TimeAxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        # interval lines
        libavg.LineNode(strokewidth=1,
                        pos1=(self.time_to_pixel(self.start_time), self.y_pos),
                        pos2=(self.time_to_pixel(self.start_time), self.y_pos + 10),
                        parent=self)
        libavg.LineNode(strokewidth=1,
                        pos1=(self.time_to_pixel(self.end_time), self.y_pos),
                        pos2=(self.time_to_pixel(self.end_time), self.y_pos + 10),
                        parent=self)
