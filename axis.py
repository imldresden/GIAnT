# -*- coding: utf-8 -*-

import libavg
import Util
from libavg import avg


class AxisNode(avg.DivNode):
    """
    Custom AxisNode with axis lines and labeling. Vertical if horizontal=False
    """

    def __init__(self, data_range, vertical=False, unit="cm", parent=None, **kwargs):
        super(AxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        """
        attributes
        """
        self.__x_pos = self.width / 2   # default vertical positioning of main axis line inside AxisNode area
        self.__y_pos = self.height / 2  # default horizontal positioning of main axis line inside AxisNode area
        self.__label_values = []        # contains the data values of the tick labels of the axis
        self.__label_pos = []           # contains the position along the axis for each label in __label_values
        self.__ticks = []               # separation lines (ticks) for axis
        self.__labels = []              # nice numbers for tick labels from __label_values
        self.__label_nodes = []         # contains WordNodes for tick labels with text values from _labels
        self.__vertical = vertical      # if True, axis is drawn vertically
        self.__start = data_range[0]    # current minimal data value of visualization data
        self.__end = data_range[1]      # current maximal data value of visualization data
        self.__unit = unit              # unit of measurement for axis values (time: h, min, s, ms, length: m, cm, mm)

        # temp rect to visualize div area
        self.rect = avg.RectNode(size=self.size, fillopacity=.1, fillcolor="FFFFFF", color="000000", parent=self)

        # create horizontal or vertical main axis line
        if self.__vertical:
            self.size = (self.size[1], self.size[0])
            libavg.LineNode(strokewidth=1, pos1=(self.__x_pos, self.height), pos2=(self.__x_pos, 0), parent=self)
        else:
            libavg.LineNode(strokewidth=1, pos1=(0, self.__y_pos), pos2=(self.width, self.__y_pos), parent=self)

        self.__update(self.__start, self.__end)

    def update(self, start, end, offset=0):
        """
        updates position of ticks and labels, and value of labels
        needs to be called whenever corresponding data is changing (e.g. in onFrame())
        """
        self.__start = start
        self.__end = end

        # calculate tick marks with R's pretty algorithm and format numbers
        self.__label_values = Util.r_pretty(dmin=self.__start, dmax=self.__end, n=5)
        self.__labels = [self.__format_label_value(v) for v in self.__label_values]

        # calculate positions of ticks within AxisNode
        offset = self._value_to_pixel(offset, 0, self.__end - self.__start)
        self.__label_pos = [self._value_to_pixel(t, 0, self.__end - self.__start) - offset for t in self.__label_values]

        self.__draw_ticks()

    def __draw_ticks(self):
        """
        draw each tick and the corresponding tick label on the position at the axis line
        """
        # delete old axis ticks
        for tick in self.__ticks:
            tick.unlink()
        self.__ticks = [None] * len(self.__label_pos)

        # delete old axis labels
        for label in self.__label_nodes:
            label.unlink()
        self.__label_nodes = [None] * len(self.__label_pos)

        # for each tick create new tick-line and value label at position on axis line
        for i, pos in enumerate(self.__label_pos):
            if type(self.__ticks[i]) is not "libavg.avg.LineNode":
                # create new axis tick and label at pos
                self.__ticks[i] = libavg.LineNode(strokewidth=1, parent=self)
                self.__label_nodes[i] = libavg.WordsNode(color="FFFFFF", parent=self)

            # set label value
            self.__label_nodes[i].text = "{}".format(self.__labels[i])

            # set position of tick and label on axis
            center = self.__label_nodes[i].width / 2
            v_center = self.__label_nodes[i].fontsize / 2
            if self.__vertical:
                self.__ticks[i].pos1 = (self.__x_pos, pos)
                self.__ticks[i].pos2 = (self.width - 5, pos)
                self.__label_nodes[i].pos = (5, pos - v_center)
            else:
                self.__ticks[i].pos1 = (pos, 5)
                self.__ticks[i].pos2 = (pos, self.__y_pos)
                self.__label_nodes[i].pos = (pos - center, 30)

    def _value_to_pixel(self, value, start, end):
        """
        calculate pixel position on axis line of label value
        """
        if self.__vertical:
            a = (end - start) / self.height
        else:
            a = (end - start) / self.width
        return value / a - start / a

    def __format_label_value(self, v):
        """
        format label values depending on units of measurement
        """

        str_v = v

        # length units in centimeters
        if self.__unit is "cm":

            meter = v / 100

            # cut zeros if value is integer
            if meter % 1 in (0, 0.0):
                meter = int(meter)
            else:
                meter = round(meter, 4)

            str_v = "{} m".format(meter)

        # time units in milliseconds
        elif self.__unit is "ms":
            # calculate seconds and minutes from milliseconds
            s, ms = divmod(v, 1000)
            m, s = divmod(s, 60)

            ms = int(ms)
            s = int(s)
            m = int(m)

            str_ms = ""
            str_s = ""
            str_m = ""

            if ms is 0 and s is 0 and m is 0:
                str_m = "0 min"
            if m > 0:
                str_m = "{} min ".format(m)

            if ms > 0:
                str_ms = "{} ms".format(self.__format_ms(ms))

            if s > 0:
                if ms > 0:
                    str_s = "{},".format(s)
                    str_ms = "{} s".format(self.__format_ms(ms))
                else:
                    str_s = "{} s ".format(s)
            else:
                if m > 0 and ms > 0:
                    str_s = "{},".format(s)
                    str_ms = "{} s".format(self.__format_ms(ms))

            str_v = "{}{}{}".format(str_m, str_s, str_ms)

        # no specific units defined
        else:
            # cut zeros if value is integer
            if v % 1 in (0, 0.0):
                v = int(v)
            # add SI prefix for one million
            if v >= 1000000:
                str_v = "{} M".format(v / 1000000)
            # add SI prefix for one thousand
            elif v >= 1000:
                str_v = "{} k".format(v / 1000)

        return str_v

    def __format_ms(self, ms):
        """
        add leading zero(s) to milliseconds if necessary
        """
        str_ms = ms
        if ms < 100:
            str_ms = "0{}".format(ms)
            if ms < 10:
                str_ms = "0{}".format(str_ms)
        return str_ms

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

    def __get_start(self):
        return self.__start

    def __get_end(self):
        return self.__end

    size = property(__getSize, __setSize)
    x_pos = property(__get_x_pos, __set_x_pos)
    y_pos = property(__get_y_pos, __set_y_pos)
    label_values = property(__get_label_values)
    start = property(__get_start)
    end = property(__get_end)

    __update = update               # private copy of original update() method
    __div_size = avg.DivNode.size   # private copy of DivNode size


class TimeAxisNode(AxisNode):
    """
    Custom TimeAxisNode with axis lines and labeling. Derived from AxisNode. Additional interval markings.
    """

    def __init__(self, parent=None, **kwargs):
        # pass arguments to super and initialize C++ class
        super(TimeAxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        """
        attributes
        """
        self.__i_start = self._value_to_pixel(self.start, self.start, self.end)   # interval start
        self.__i_end = self._value_to_pixel(self.start, self.start, self.end)     # interval end
        self.__i_start_line = None                                                # LineNode for begin of interval
        self.__i_end_line = None                                                  # LineNode for end of interval

        # interval lines
        self.__i_start_line = libavg.LineNode(strokewidth=2, color="FF0000",
                                              pos1=(self.__i_start, self.y_pos), pos2=(self.__i_start, self.y_pos - 15),
                                              parent=self)
        self.__i_end_line = libavg.LineNode(strokewidth=2, color="FF0000",
                                            pos1=(self.__i_end, self.y_pos), pos2=(self.__i_end, self.y_pos - 15),
                                            parent=self)

        self.update(self.start, self.end, self.start, self.end)

    def update(self, start, end, interval_start, interval_end):
        """
        updates position of interval start and interval end
        needs to be called whenever corresponding data is changing (e.g. in onFrame())
        """
        # set new interval start and end
        self.__i_start = self._value_to_pixel(interval_start, start, end)
        self.__i_end = self._value_to_pixel(interval_end, start, end)

        # update positions of interval lines
        self.__i_start_line.pos1 = (self.__i_start, self.__i_start_line.pos1[1])
        self.__i_start_line.pos2 = (self.__i_start, self.__i_start_line.pos2[1])
        self.__i_end_line.pos1 = (self.__i_end, self.__i_end_line.pos1[1])
        self.__i_end_line.pos2 = (self.__i_end, self.__i_end_line.pos2[1])
