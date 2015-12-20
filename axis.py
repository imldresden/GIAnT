# -*- coding: utf-8 -*-

import libavg
from global_values import global_values
from libavg import avg


class AxisNode(avg.DivNode):
    """
    Custom AxisNode with axis lines and labeling. Vertical if horizontal=False
    """

    __div_size = avg.DivNode.size

    def __init__(self, horizontal=True, parent=None, **kwargs):
        super(AxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        """
        attributes
        """
        self.__x_pos = self.width / 2   # default vertical positioning of main axis line inside AxisNode area
        self.__y_pos = self.height / 2  # default horizontal positioning of main axis line inside AxisNode area
        self.values = global_values()   # has total and interval time data

        # temp rect to visualize div area
        self.rect = avg.RectNode(size=self.size, fillopacity=.1, fillcolor="FFFFFF", color="000000", parent=self)

        # create horizontal or vertical main axis line
        if horizontal:
            libavg.LineNode(strokewidth=1, pos1=(0, self.__y_pos), pos2=(self.width, self.__y_pos), parent=self)
        else:
            self.size = (self.size[1], self.size[0])
            libavg.LineNode(strokewidth=1, pos1=(self.__x_pos, self.height), pos2=(self.__x_pos, 0), parent=self)

    def time_to_pixel(self, time):
        return time / ((self.values.total_end_time - self.values.total_start_time) / self.width)

    def __r_pretty(self, min, max, classes):
        """
        TODO
        """
        return min

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

    size = property(__getSize, __setSize)
    x_pos = property(__get_x_pos, __set_x_pos)
    y_pos = property(__get_y_pos, __set_y_pos)


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