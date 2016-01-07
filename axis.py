# -*- coding: utf-8 -*-

import libavg
import Util
import global_values
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
        self.__h_tick_length = 5                             # half of the length of the tick marks on the axis
        self.__tick_length = self.__h_tick_length * 2        # length of the tick marks on the axis
        self.__x_offset = self.width - self.__h_tick_length  # offset of vertical line from right edge of DivNode
        self.__y_offset = self.__h_tick_length               # offset of horizontal line from upper edge of DivNode
        self.__label_offset = 5                              # offset of tick labels from axis line
        self.__label_values = []                             # contains the data values of the tick labels of the axis
        self.__label_pos = []                                # contains the pos at axis for each label in __label_values
        self.__ticks = []                                    # separation lines (ticks) for axis
        self.__labels = []                                   # nice numbers for tick labels from __label_values
        self.__label_nodes = []                              # WordNodes for tick labels with values from _labels
        self.__grid = []                                     # contains the grid lines covering the visualization
        self.__vertical = vertical                           # if True, axis is drawn vertically
        self.__start = data_range[0]                         # current minimal data value of visualization data
        self.__end = data_range[1]                           # current maximal data value of visualization data
        self.__unit = unit                                   # unit of measurement (time: ms, length: cm)

        # background rectangle
        self.rect = avg.RectNode(size=self.size, fillopacity=.0, fillcolor="FFFFFF", color="000000", parent=self)

        # create horizontal or vertical main axis line
        if self.__vertical:
            self.size = (self.size[1], self.size[0])
            self.__x_offset = self.width - self.__h_tick_length
            libavg.LineNode(strokewidth=1, pos1=(self.__x_offset, self.height), pos2=(self.__x_offset, 0), parent=self)
        else:
            libavg.LineNode(strokewidth=1, pos1=(0, self.__y_offset), pos2=(self.width, self.__y_offset), parent=self)

        self.__update(self.__start, self.__end)

    def update(self, start, end, offset=0):
        """
        updates position of ticks and labels, and value of labels
        needs to be called whenever corresponding data is changing (e.g. in onFrame())
        """
        self.__start = start
        self.__end = end

        # calculate tick marks with R's pretty algorithm and format numbers
        if self.__unit is "ms":
            self.__label_values = Util.r_pretty(dmin=self.__start, dmax=self.__end, n=5, time=True)
        else:
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

        # delete old grid lines
        for grid in self.__grid:
            grid.unlink()
        self.__grid = [None] * len(self.__label_pos)

        # for each tick create new tick-line, value label and grid line at position on axis line
        for i, pos in enumerate(self.__label_pos):
            if type(self.__ticks[i]) is not "libavg.avg.LineNode":
                # create new axis tick and label at pos
                self.__ticks[i] = libavg.LineNode(strokewidth=1, parent=self)
                self.__label_nodes[i] = libavg.WordsNode(color="FFFFFF", parent=self)
                self.__grid[i] = libavg.LineNode(strokewidth=1, color="222222", parent=self)

            # set label value
            self.__label_nodes[i].text = "{}".format(self.__labels[i])

            # set position of tick and label on axis
            center = self.__label_nodes[i].width / 2
            v_center = self.__label_nodes[i].fontsize / 2
            if self.__vertical:
                self.__ticks[i].pos1 = (self.__x_offset - self.__h_tick_length, pos)
                self.__ticks[i].pos2 = (self.__x_offset + self.__h_tick_length, pos)
                self.__label_nodes[i].pos = (self.__x_offset - 40, pos - v_center - 1)
                self.__grid[i].pos1 = (self.__ticks[i].pos1[0], pos)
                self.__grid[i].pos2 = (1500, pos)
            else:
                self.__ticks[i].pos1 = (pos, self.__y_offset - self.__tick_length)
                self.__ticks[i].pos2 = (pos, self.__y_offset)
                self.__label_nodes[i].pos = (pos - center, self.__y_offset + self.__h_tick_length + self.__label_offset)
                self.__grid[i].pos1 = (pos, self.__ticks[i].pos1[1])
                self.__grid[i].pos2 = (pos, - 750)

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

    def __get_x_offset(self):
        return self.__x_offset

    def __set_x_offset(self, x):
        self.__x_offset = x

    def __get_y_offset(self):
        return self.__y_offset

    def __set_y_offset(self, y):
        self.__y_offset = y

    def __get_label_values(self):
        return self.__label_values

    def __get_start(self):
        return self.__start

    def __get_end(self):
        return self.__end

    def __get_h_tick_length(self):
        return self.__h_tick_length

    def __get_tick_length(self):
        return self.__tick_length

    def __get_label_offset(self):
        return self.__label_offset

    def __set_label_offset(self, offset):
        self.__label_offset = offset

    size = property(__getSize, __setSize)
    x_offset = property(__get_x_offset, __set_x_offset)
    y_offset = property(__get_y_offset, __set_y_offset)
    label_values = property(__get_label_values)
    start = property(__get_start)
    end = property(__get_end)
    h_tick_length = property(__get_h_tick_length)
    tick_length = property(__get_tick_length)
    label_offset = property(__get_label_offset, __set_label_offset)

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
        self.__i_start = self._value_to_pixel(self.start, self.start, self.end) # interval start
        self.__i_end = self._value_to_pixel(self.start, self.start, self.end)   # interval end
        self.label_offset = 10                                                  # bigger label offset for time axis

        # interval lines
        self.__i_start_interval_line = libavg.LineNode(strokewidth=1, color="333333", parent=self,
                                                       pos1=(0, self.y_offset + self.tick_length),
                                                       pos2=(self.__i_end, self.y_offset + self.tick_length))
        self.__i_end_interval_line = libavg.LineNode(strokewidth=1, color="333333", parent=self,
                                                     pos1=(self.width, self.y_offset + self.tick_length),
                                                     pos2=(self.end, self.y_offset + self.tick_length))
        self.__i_line = libavg.LineNode(strokewidth=5, color="FFFFFF", parent=self,
                                        pos1=(self.start, self.y_offset + self.tick_length - 2),
                                        pos2=(self.end, self.y_offset + self.tick_length - 2))

        self.update(self.start, self.end)

    def update(self, i_start, i_end, offset=0):
        """
        updates position of interval start and interval end
        needs to be called whenever corresponding data is changing (e.g. in onFrame())
        """
        # set new interval start and end
        self.__i_start = self._value_to_pixel(i_start, global_values.total_range[0], global_values.total_range[1])
        self.__i_end = self._value_to_pixel(i_end, global_values.total_range[0], global_values.total_range[1])

        # update positions of interval lines
        self.__i_start_interval_line.pos2 = (self.__i_start, self.__i_start_interval_line.pos2[1])
        self.__i_end_interval_line.pos2 = (self.__i_end, self.__i_end_interval_line.pos2[1])
        self.__i_line.pos1 = (self.__i_start, self.__i_line.pos1[1])
        self.__i_line.pos2 = (self.__i_end, self.__i_line.pos2[1])

        super(TimeAxisNode, self).update(i_start, i_end, offset)
