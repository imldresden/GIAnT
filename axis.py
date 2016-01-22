# -*- coding: utf-8 -*-

import math
import libavg
import Time_Frame
import custom_slider
import global_values
from libavg import avg

AXIS_THICKNESS = 50


class AxisNode(avg.DivNode):
    """
    Custom AxisNode with axis lines and labeling. Vertical if horizontal=False
    """

    def __init__(self, data_range, unit="cm", parent=None, **kwargs):
        super(AxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        """
        attributes
        """
        self.__h_tick_length = 5                             # half of the length of the tick marks on the axis
        self.__tick_length = self.__h_tick_length * 2        # length of the tick marks on the axis
        self.__label_offset = self.__tick_length             # offset of tick labels from axis line
        self.__label_values = []                             # contains the data values of the tick labels of the axis
        self.__label_pos = []                                # contains the pos at axis for each label in __label_values
        self.__ticks = []                                    # separation lines (ticks) for axis
        self.__labels = []                                   # nice numbers for tick labels from __label_values
        self.__label_nodes = []                              # WordNodes for tick labels with values from _labels
        self.__grid = []                                     # contains the grid lines covering the visualization
        self.__vertical = False                              # if True, axis is drawn vertically
        self.__data_range = data_range                       # data range of data set
        self.__start = data_range[0]                         # current minimal data value of visualization data
        self.__end = data_range[1]                           # current maximal data value of visualization data
        self.__unit = unit                                   # unit of measurement (time: ms, length: cm)

        # axis is displayed vertical if width smaller than height
        if self.height > self.width:
            self.__vertical = True

        # create main axis line (horizontal or vertical)
        self.__axis_line = libavg.LineNode(strokewidth=1, parent=self)
        if self.__vertical:
            self.__axis_line.pos1 = (self.width, 0)
            self.__axis_line.pos2 = (self.width, self.height)
        else:
            self.__axis_line.pos1 = (0, 0)
            self.__axis_line.pos2 = (self.width, 0)

        # initial update
        self.__update(self.__start, self.__end)

    def update(self, start, end):
        """
        updates position of ticks and labels, and value of labels
        needs to be called whenever corresponding data is changing (e.g. in onFrame())
        """
        self.__start = start
        self.__end = end

        # calculate tick marks with R's pretty algorithm and format numbers
        if self.__unit is "ms":
            self.__label_values = r_pretty(dmin=self.__start, dmax=self.__end, n=5, time=True)
        else:
            self.__label_values = r_pretty(dmin=self.__start, dmax=self.__end, n=5)
        self.__labels = [self._format_label_value(v) for v in self.__label_values]

        # calculate positions of ticks within AxisNode
        offset = self._value_to_pixel(start, 0, self.__end - self.__start)
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
                # create new axis tick, label and grid line
                self.__grid[i] = libavg.LineNode(strokewidth=1, color=global_values.COLOR_SECONDARY, parent=self)
                self.__ticks[i] = libavg.LineNode(strokewidth=1, color=global_values.COLOR_FOREGROUND, parent=self)
                self.__label_nodes[i] = libavg.WordsNode(color=global_values.COLOR_FOREGROUND, parent=self)

            # set label value
            self.__label_nodes[i].text = "{}".format(self.__labels[i])

            # set position of tick, label and grid on axis
            center = self.__label_nodes[i].width / 2
            v_center = self.__label_nodes[i].fontsize / 2
            if self.__vertical:
                self.__label_nodes[i].alignment = "right"
                self.__grid[i].pos1 = (self.__axis_line.pos1[0], pos)
                self.__grid[i].pos2 = (self.parent.pos[0] + self.parent.width, pos)
                self.__ticks[i].pos1 = (self.__axis_line.pos1[0], pos)
                self.__ticks[i].pos2 = (self.__axis_line.pos1[0] + self.__tick_length, pos)
                self.__label_nodes[i].pos = (self.__axis_line.pos1[0] - self.__tick_length, pos - v_center - 1)
            else:
                self.__grid[i].pos1 = (pos, self.__axis_line.pos1[0])
                # TODO: get visualization height
                self.__grid[i].pos2 = (pos, -600)
                self.__ticks[i].pos1 = (pos, self.__axis_line.pos1[0] - self.__tick_length)
                self.__ticks[i].pos2 = (pos, self.__axis_line.pos1[0])
                self.__label_nodes[i].pos = (pos - center,
                                             self.__axis_line.pos1[0] + self.__h_tick_length + self.__label_offset)

        # delete first and last tick except it is min or max of data range
        if self.__label_values[0] not in self.__data_range:
            self.__grid[0].unlink()
            self.__ticks[0].unlink()
            self.__label_nodes[0].unlink()

        if self.__label_values[len(self.__label_values) - 1] not in self.__data_range:
            self.__grid[len(self.__label_values) - 1].unlink()
            self.__ticks[len(self.__label_values) - 1].unlink()
            self.__label_nodes[len(self.__label_values) - 1].unlink()

    def _value_to_pixel(self, value, start, end):
        """
        calculate pixel position on axis line of label value
        """
        if self.__vertical:
            a = (end - start) / self.height
        else:
            a = (end - start) / self.width
        return value / a - start / a

    def _format_label_value(self, v):
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
        self.__div_size = size

    def __get_vertical(self):
        return self.__vertical

    def __set_vertical(self, v):
        self.__vertical = v

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

    def __get_data_range(self):
        return self.__data_range

    size = property(__getSize, __setSize)
    vertical = property(__get_vertical, __set_vertical)
    label_values = property(__get_label_values)
    start = property(__get_start)
    end = property(__get_end)
    h_tick_length = property(__get_h_tick_length)
    tick_length = property(__get_tick_length)
    label_offset = property(__get_label_offset, __set_label_offset)
    data_range = property(__get_data_range)

    __update = update               # private copy of original update() method
    __div_size = avg.DivNode.size   # private copy of DivNode size


class TimeAxisNode(AxisNode):
    """
    Custom TimeAxisNode with axis lines, labeling and an interval line and slider.
    """

    def __init__(self, parent=None, **kwargs):
        """
        Initialize time axis node and setup specific child nodes.
        :param parent: where this node is parented to
        """
        # pass arguments to super and initialize C++ class
        super(TimeAxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        """
        attributes
        """
        self.__i_start = self._value_to_pixel(self.start, self.start, self.end)  # interval start
        self.__i_end = self._value_to_pixel(self.end, self.start, self.end)      # interval end
        self.__i_label_offset = 5                                                # offset for interval duration label
        self.label_offset = 1.5 * self.tick_length                               # bigger label offset for time axis
        self.vertical = False                                                    # TimeAxisNode can only be horizontal

        """
        setup Nodes
        """
        # interval lines and rectangle
        self.__i_line = libavg.LineNode(strokewidth=1, color=global_values.COLOR_SECONDARY, parent=self,
                                        pos1=(0, 1.5 * self.tick_length),
                                        pos2=(self.width, 1.5 * self.tick_length))
        self.__i_rect = libavg.RectNode(strokewidth=0, fillopacity=1, parent=self,
                                        color=global_values.COLOR_FOREGROUND, fillcolor=global_values.COLOR_FOREGROUND,
                                        pos=(self.__i_start, 1.5 * self.tick_length),
                                        size=(self.__i_end - self.__i_start, -5))
        # vertical brushing & linking line
        self.__highlight_line = libavg.LineNode(strokewidth=1, color=global_values.COLOR_FOREGROUND, parent=self,
                                                pos1=(0, 0), pos2=(0, -self.parent.height))
        # interactive interval scrollbar
        self.__i_scrollbar = custom_slider.IntervalScrollBar(pos=(0, 3), width=self.width, opacity=0,
                                                             range=self.data_range, parent=self)
        # label for total interval time range
        self.__i_label = libavg.WordsNode(color=global_values.COLOR_BACKGROUND, text="", opacity=0, sensitive=False,
                                          parent=self)

        """
        subscriptions
        """
        # change of thumb pos of interval slider
        self.__i_scrollbar.subscribe(custom_slider.IntervalScrollBar.THUMB_POS_CHANGED,
                                     lambda pos: self.__change_interval(self.__i_scrollbar.getThumbPos(),
                                                                        self.end + pos - self.start))
        # subscription for mouse movement over visualization (highlight line)
        self.getParent().subscribe(avg.Node.CURSOR_MOTION, self.__on_visualization_hover_over)
        # subscription to mouse click to highlight single user path
        # for i in range(self.getParent().getNumChildren()):
        #     print type(self.getParent().getChild(i))
        #     if type(self.getParent().getChild(i)) is "libavg.avg.MeshNode":
        #         self.getParent().getChild(i).subscribe(avg.Node.CURSOR_DOWN, self.__on_path_click)
        # more/less details of interval slider
        self.subscribe(avg.Node.CURSOR_OVER, self.__show_interval_slider)
        self.subscribe(avg.Node.CURSOR_OUT, self.__hide_interval_slider)
        # show/hide highlight line over visualization
        self.getParent().subscribe(avg.Node.CURSOR_OVER, self.__show_highlight_line)
        self.getParent().subscribe(avg.Node.CURSOR_OUT, self.__hide_highlight_line)
        # subscribe to global time frame publisher
        Time_Frame.main_time_frame.subscribe(self)

        """
        initial update
        """
        self.update(self.start, self.end)

    def __on_path_click(self, event=None):
        print "{}".format(event.node)

    def update_time_frame(self, interval):
        """
        Called by the publisher time_frame to update the visualization to the new interval.
        :param interval: (start, end): new interval start and end as list
        """
        self.update(interval[0], interval[1])

    def __change_interval(self, start, end):
        """
        Changes interval by publishing the new interval start and end to time_frame.
        Called whenever the interval needs to be changed by user input (e.g. when interval slider is dragged).
        :param start: new interval start
        :param end: new interval end
        :return: new interval start
        """
        # update axis
        self.update(start, end)

        # update time frame
        Time_Frame.main_time_frame.set_time_frame((start, end))

        # update ScrollBar size
        new_thumb_pos = start
        return new_thumb_pos

    def update(self, i_start, i_end):
        """
        Updates position of interval start and interval end.
        Needs to be called whenever corresponding data is changing (e.g. in onFrame()).
        :param i_start: new interval start
        :param i_end: new interval end
        """
        # set new interval start and end
        self.__i_start = self._value_to_pixel(i_start, Time_Frame.total_range[0], Time_Frame.total_range[1])
        self.__i_end = self._value_to_pixel(i_end, Time_Frame.total_range[0], Time_Frame.total_range[1])

        # update positions of interval lines
        self.__i_rect.pos = (self.__i_start, self.__i_rect.pos[1])
        self.__i_rect.size = (self.__i_end - self.__i_start, self.__i_rect.size[1])

        # call update from AxisNode (updates self.end and self.start)
        super(TimeAxisNode, self).update(i_start, i_end)

        # update interval details on demand (hover over)
        self.__i_label.text = "{}".format(self._format_label_value(self.end - self.start))
        if self.__i_rect.size[0] > self.__i_label.width + self.__i_label_offset:
            self.__i_label.color = global_values.COLOR_BACKGROUND
            self.__i_label.pos = (self.__i_rect.pos[0] + self.__i_rect.size[0] / 2 - self.__i_label.width / 2, 2)
        else:
            self.__i_label.color = global_values.COLOR_FOREGROUND
            if self.__i_rect.pos[0] > self.__i_label.width + self.__i_label_offset:
                self.__i_label.pos = (self.__i_rect.pos[0] - self.__i_label.width - self.__i_label_offset, 2)
            else:
                self.__i_label.pos = (self.__i_rect.pos[0] + self.__i_rect.size[0] + self.__i_label_offset, 2)

        # update scrollbar
        self.__i_scrollbar.setThumbPos(self.start)
        self.__i_scrollbar.setThumbExtent(self.end - self.start)

    def __show_interval_slider(self, event=None):
        """
        Called when mouse hovers over TimeAxisNodeDiv. Shows Details on demand of interval.
        """
        # make interval rect bigger
        self.__i_rect.size = (self.__i_rect.size[0], -13)
        self.__i_rect.pos = (self.__i_rect.pos[0], self.__i_rect.pos[1] + 3)
        # show label with current total interval time
        self.__i_label.opacity = 1
        # show interval scrollbar
        self.__i_scrollbar.opacity = 1

    def __hide_interval_slider(self, event=None):
        """
        Hide Details on Demand of interval when mouse hovers out of TimeAxisNodeDiv area.
        """
        # make interval rect normal size again
        self.__i_rect.size = (self.__i_rect.size[0], -5)
        self.__i_rect.pos = (self.__i_rect.pos[0], self.__i_rect.pos[1] - 3)
        # hide label with current total interval time
        self.__i_label.opacity = 0
        # hide interval scrollbar
        self.__i_scrollbar.opacity = 0

    def __on_visualization_hover_over(self, event=None):
        """
        Moves the highlight line along the vertical mouse position.
        """
        relPos = self.getRelPos(event.pos)
        self.__highlight_line.pos1 = (relPos[0], self.__highlight_line.pos1[1])
        self.__highlight_line.pos2 = (relPos[0], self.__highlight_line.pos2[1])
        # let line appear in front of every other child in this div
        self.removeChild(self.__highlight_line)
        self.appendChild(self.__highlight_line)

    def __show_highlight_line(self, event=None):
        self.__highlight_line.opacity = 1

    def __hide_highlight_line(self, event=None):
        self.__highlight_line.opacity = 0

"""
utils
"""


def r_pretty(dmin, dmax, n, time=False):
    """
    calculates "nice" ticks for axis
    """

    min_n = int(n / 3)                          # non-negative integer giving minimal number of intervals n
    shrink_small = 0.75                         # positive numeric by which a default scale is shrunk
    high_unit_bias = 1.5                        # non-negative numeric, typically > 1
                                                # the interval unit is determined as {1,2,5,10} * b, a power of 10
                                                # larger high_unit_bias favors larger units
    unit5_bias = 0.5 + 1.5 * high_unit_bias     # non-negative numeric multiplier favoring factor 5 over 2

    h = high_unit_bias
    h5 = unit5_bias
    ndiv = n

    dx = dmax - dmin

    if dx is 0 and dmax is 0:
        cell = 1.0
        i_small = True
        u = 1
    else:
        cell = max(abs(dmin), abs(dmax))
        if h5 >= 1.5 * h + 0.5:
            u = 1 + (1.0 / (1 + h))
        else:
            u = 1 + (1.5 / (1 + h5))
        i_small = dx < (cell * u * max(1.0, ndiv) * 1e-07 * 3.0)

    if i_small:
        if cell > 10:
            cell = 9 + cell / 10
            cell *= shrink_small
        if min_n > 1:
            cell /= min_n
    else:
        cell = dx
        if ndiv > 1:
            cell /= ndiv
    if cell < 20 * 1e-07:
        cell = 20 * 1e-07

    base = 10.00**math.floor(math.log10(cell))
    unit = base

    # time values have different preferred values
    if time:
        if (2 * base) - cell < h * (cell - unit):
            unit = 2.0 * base
            if (3 * base) - cell < h * (cell - unit):
                unit = 3.0 * base
                if (6 * base) - cell < h5 * (cell - unit):
                    unit = 6.0 * base
                    if (10 * base) - cell < h * (cell - unit):
                        unit = 10.0 * base
    else:
        if (2 * base) - cell < h * (cell - unit):
            unit = 2.0 * base
            if (5 * base) - cell < h5 * (cell - unit):
                unit = 5.0 * base
                if (10 * base) - cell < h * (cell - unit):
                    unit = 10.0 * base

    ns = math.floor(dmin / unit + 1e-07)
    nu = math.ceil(dmax / unit - 1e-07)

    # extend range out beyond the data
    while ns * unit > dmin + (1e-07 * unit):
        ns -= 1
    while nu * unit < dmax - (1e-07 * unit):
        nu += 1

    # if not enough labels, extend range out to make more (labels beyond data!)
    k = math.floor(0.5 + nu-ns)
    if k < min_n:
        k = min_n - k
        if ns >= 0:
            nu += k / 2
            ns = ns - k / 2 + k % 2
        else:
            ns -= k / 2
            nu = nu + k / 2 + k % 2
        ndiv = min_n
    else:
        ndiv = k

    graphmin = ns * unit
    graphmax = nu * unit
    count = int(math.ceil(graphmax - graphmin) / unit)
    res = [graphmin + k * unit for k in range(count + 1)]
    if res[0] < dmin:
        res[0] = dmin
    if res[-1] > dmax:
        res[-1] = dmax
    return res
