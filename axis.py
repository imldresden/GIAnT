# -*- coding: utf-8 -*-

import math
import libavg
import util
import custom_slider
import global_values
from libavg import avg

THICKNESS = 50     # space needed for axis display (means height if axis is horizontal, width otherwise)


class AxisNode(avg.DivNode):
    def __init__(self, data_range, unit="cm", hide_rims=False, top_axis=False, inverted=False, parent=None,
                 label_offset=0, **kwargs):
        """
        Custom AxisNode with axis lines, grid lines and labeling.
        :param data_range: The minimum and maximum data range to be displayed
        :param unit: Unit of measurement (time: ms, length: cm)
        :param hide_rims: Hides first and last ticks if True
        :param top_axis: Determines if a slimmed x-axis should be displayed at the top instead of the bottom
        :param inverted: If True, values on axis are displayed inverted
        :param parent: The parent DivNode
        :param kwargs: Other parameters needed for a DivNode
        """
        super(AxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        """attributes"""
        self.__parent = parent
        self.__top_axis = top_axis                           # determines if the x-axis should be displayed at the top
        if self.__top_axis:
            self.__h_tick_length = -5                        # half of the length of the tick marks on the axis
        else:
            self.__h_tick_length = 5
        self.__tick_length = self.__h_tick_length * 2        # length of the tick marks on the axis
        self.__label_offset = label_offset                   # offset of tick labels from axis line
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
        self.__hide_rims = hide_rims                         # determines if the first and last tick are shown
        self.__inverted = inverted                           # shows values on axis inverted if true

        """
        TODO:
        Workaround for not working self.__parent.data_div.height for yet unknown reasons.
        The workaround should set the height when initializing a time axis.
        """
        try:
            self.__vis_height = self.__parent.data_div.height
        except:
            self.__vis_height = 0
            if isinstance(self, TimeAxisNode):
                # workaround in TimeAxisNode!
                pass
            else:
                print "Info: Could not get height of data_div in {}!".format(self)

        # axis is displayed vertical if width smaller than height
        if self.height > self.width:
            self.__vertical = True
            self.width = THICKNESS
        else:
            self.height = THICKNESS

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
        :param start: start value in unit of measurement (not in pixel)
        :param end: end value in unit of measurement (not in pixel)
        """
        self.__start = start
        self.__end = end

        # calculate tick marks with R's pretty algorithm and format numbers
        if self.__unit is "ms":
            self.__label_values = r_pretty(dmin=self.__start, dmax=self.__end, n=5, time=True)
        else:
            self.__label_values = r_pretty(dmin=self.__start, dmax=self.__end, n=5)
        self.__labels = [util.format_label_value(self.__unit, v) for v in self.__label_values]

        # calculate positions of ticks within AxisNode
        if self.__inverted:
            offset = self._value_to_pixel(end, 0, self.__end - self.__start)
        else:
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
                self.__grid[i] = libavg.LineNode(strokewidth=1, color=global_values.COLOR_BACKGROUND, parent=self)
                self.__ticks[i] = libavg.LineNode(strokewidth=1, color=global_values.COLOR_FOREGROUND, parent=self)
                if not self.__top_axis:
                    self.__label_nodes[i] = libavg.WordsNode(color=global_values.COLOR_FOREGROUND, parent=self)

            # set label value
            if not self.__top_axis:
                self.__label_nodes[i].text = "{}".format(self.__labels[i])

            # set position of tick, label and grid on axis
            center = 0
            v_center = 0
            if not self.__top_axis:
                center = self.__label_nodes[i].width / 2
                v_center = self.__label_nodes[i].fontsize / 2
            if self.__vertical:
                self.__grid[i].pos1 = (self.__axis_line.pos1[0], pos)
                self.__grid[i].pos2 = (self.__axis_line.pos1[0] + self.parent.data_div.width, pos)
                self.__ticks[i].pos1 = (self.__axis_line.pos1[0], pos)
                self.__ticks[i].pos2 = (self.__axis_line.pos1[0] + self.__tick_length, pos)
                if not self.__top_axis:
                    self.__label_nodes[i].alignment = "right"
                    self.__label_nodes[i].pos = (self.__axis_line.pos1[0] - self.__tick_length - self.__label_offset,
                                                 pos - v_center - 1)
            else:
                self.__grid[i].pos1 = (pos, self.__axis_line.pos1[0])
                if self.__top_axis:
                    self.__grid[i].pos2 = (pos, + self.__vis_height)
                else:
                    self.__grid[i].pos2 = (pos, - self.__vis_height)
                self.__ticks[i].pos1 = (pos, self.__axis_line.pos1[0] - self.__tick_length)
                self.__ticks[i].pos2 = (pos, self.__axis_line.pos1[0])
                if not self.__top_axis:
                    self.__label_nodes[i].pos = (pos - center,
                                                 self.__axis_line.pos1[0] + self.__h_tick_length + self.__label_offset)

        # delete first and last grid line (because it is not really needed and can overlap other axis lines)
        self.__grid[0].unlink()
        self.__grid[len(self.__label_values) - 1].unlink()

        # delete first and last tick except it is min or max of data range
        if self.__label_values[0] not in self.__data_range or self.__hide_rims:
            self.__ticks[0].unlink()
            if not self.__top_axis:
                self.__label_nodes[0].unlink()
        if self.__label_values[len(self.__label_values) - 1] not in self.__data_range or self.__hide_rims:
            self.__ticks[len(self.__label_values) - 1].unlink()
            if not self.__top_axis:
                self.__label_nodes[len(self.__label_values) - 1].unlink()

    def _value_to_pixel(self, value, start, end):
        """
        Calculate pixel position on axis line of label value.
        :param value: Value in unit of measurement
        :param start: start value in unit of measurement
        :param end: end value in unit of measurement
        :return: pixel position of value
        """
        if self.__vertical:
            length = self.height
        else:
            length = self.width

        a = (end - start) / length
        pixel_pos = value / a - start / a

        if self.__inverted:
            return length - pixel_pos
        else:
            return pixel_pos

    """python properties"""
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

    def __get_vis_height(self):
        return self.__vis_height

    def __set_vis_height(self, height):
        self.__vis_height = height

    def __get_unit(self):
        return self.__unit

    size = property(__getSize, __setSize)
    vertical = property(__get_vertical, __set_vertical)
    label_values = property(__get_label_values)
    start = property(__get_start)
    end = property(__get_end)
    h_tick_length = property(__get_h_tick_length)
    tick_length = property(__get_tick_length)
    label_offset = property(__get_label_offset, __set_label_offset)
    data_range = property(__get_data_range)
    vis_height = property(__get_vis_height, __set_vis_height)
    unit = property(__get_unit)

    __update = update               # private copy of original update() method
    __div_size = avg.DivNode.size   # private copy of DivNode size


class TimeAxisNode(AxisNode):
    """
    Custom TimeAxisNode with axis lines, labeling and an interval line and slider.
    """

    def __init__(self, vis_params, parent=None, **kwargs):
        super(TimeAxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.__vis_params = vis_params
        self.__i_start = self._value_to_pixel(self.start, self.start, self.end)  # interval start
        self.__i_end = self._value_to_pixel(self.end, self.start, self.end)      # interval end
        self.__i_label_offset = 5                                                # offset for interval duration label
        self.__pinned = False                                                    # if highlight line is pinned
        self.__highlight_pixel = 0                                               # pixel position on axis of highlight
        self.label_offset = 0                                                    # smaller label offset for time axis
        self.vertical = False                                                    # TimeAxisNode can only be horizontal
        self.vis_height = self.parent.data_div.height                            # workaround (see comment in AxisNode)

        """setup Nodes"""
        # interval lines and rectangle
        self.__i_line = libavg.LineNode(strokewidth=1, color=global_values.COLOR_SECONDARY, parent=self,
                                        pos1=(0, 2.5 * self.tick_length),
                                        pos2=(self.width, 2.5 * self.tick_length))
        self.__i_rect = libavg.RectNode(strokewidth=0, fillopacity=1, parent=self,
                                        color=global_values.COLOR_FOREGROUND, fillcolor=global_values.COLOR_FOREGROUND,
                                        pos=(self.__i_start, 2.5 * self.tick_length),
                                        size=(self.__i_end - self.__i_start, 5))
        # vertical brushing & linking line
        self.__highlight_line = libavg.LineNode(strokewidth=1, color=global_values.COLOR_SECONDARY, parent=self,
                                                pos1=(0, 0), pos2=(0, -self.parent.data_div.height), opacity=0)
        self.__highlight_marker = libavg.LineNode(strokewidth=1, color=global_values.COLOR_FOREGROUND, parent=self,
                                                  pos1=(0, self.__i_line.pos1[1]), pos2=(0, self.__i_line.pos1[1] + 5),
                                                  opacity=0)
        # interactive interval scrollbar
        self.__i_scrollbar = custom_slider.IntervalScrollBar(pos=(0, self.__i_rect.pos[1]), width=self.width, opacity=0,
                                                             range=self.data_range, parent=self)
        # label for total interval time range
        self.__i_label = libavg.WordsNode(color=global_values.COLOR_BACKGROUND, text="", opacity=0, sensitive=False,
                                          parent=self)

        """subscriptions"""
        # change of thumb pos of interval slider
        self.__i_scrollbar.subscribe(custom_slider.IntervalScrollBar.THUMB_POS_CHANGED,
                                     lambda pos: self.__change_interval(self.__i_scrollbar.getThumbPos(),
                                                                        self.end + pos - self.start))
        # subscription for mouse movement over visualization (highlight line)
        self.__hover_id = self.parent.data_div.subscribe(avg.Node.CURSOR_MOTION, self.__on_visualization_hover_over)
        # pin and unpin highlight_line on mouse click
        self.parent.data_div.subscribe(avg.Node.CURSOR_DOWN, self.__toggle_pin_highlight_line)
        # more/less details of interval slider
        self.subscribe(avg.Node.CURSOR_OVER, self.__show_interval_slider)
        self.subscribe(avg.Node.CURSOR_OUT, self.__hide_interval_slider)
        # show/hide highlight line over visualization
        self.parent.data_div.subscribe(avg.Node.CURSOR_OVER, self.__show_highlight_line)
        self.parent.data_div.subscribe(avg.Node.CURSOR_OUT, self.__hide_highlight_line)
        # subscribe to global time frame publisher
        self.__vis_params.subscribe(self.__vis_params.CHANGED, self.update_time)

        """initial update"""
        self.update(self.start, self.end)

    def update_time(self, vis_params, draw_lines):
        """
        Called by the publisher time_frame to update the visualization to the new interval.
        :param interval: (start, end): new interval start and end as list
        :param draw_lines: if lines should be redrawn
        """
        interval = vis_params.get_time_interval()
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
        self.__vis_params.set_time_interval((start, end))

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
        total_range = self.__vis_params.get_total_range()
        self.__i_start = self._value_to_pixel(i_start, total_range[0], total_range[1])
        self.__i_end = self._value_to_pixel(i_end, total_range[0], total_range[1])

        # update positions of interval lines
        self.__i_rect.pos = (self.__i_start, self.__i_rect.pos[1])
        self.__i_rect.size = (self.__i_end - self.__i_start, self.__i_rect.size[1])

        # call update from AxisNode (updates self.end and self.start)
        super(TimeAxisNode, self).update(i_start, i_end)

        # update interval details on demand (hover over)
        self.__i_label.text = "{}".format(util.format_label_value(self.unit, self.end - self.start, True))
        if self.__i_rect.size[0] > self.__i_label.width + self.__i_label_offset:
            self.__i_label.color = global_values.COLOR_BACKGROUND
            self.__i_label.pos = (self.__i_rect.pos[0] + self.__i_rect.size[0] / 2 - self.__i_label.width / 2,
                                  self.__i_rect.pos[1])
        else:
            self.__i_label.color = global_values.COLOR_FOREGROUND
            if self.__i_rect.pos[0] > self.__i_label.width + self.__i_label_offset:
                self.__i_label.pos = (self.__i_rect.pos[0] - self.__i_label.width - self.__i_label_offset,
                                      self.__i_rect.pos[1])
            else:
                self.__i_label.pos = (self.__i_rect.pos[0] + self.__i_rect.size[0] + self.__i_label_offset,
                                      self.__i_rect.pos[1])

        # update scrollbar
        self.__i_scrollbar.setThumbPos(self.start)
        self.__i_scrollbar.setThumbExtent(self.end - self.start)

        # update position of pinned highlight line and highlight line marker
        if self.__pinned:
            self.__highlight_pixel = self._value_to_pixel(self.__vis_params.highlight_time,
                                                          self.start, self.end)
            if self.__highlight_pixel > self.width or self.__highlight_pixel < 0:
                self.__highlight_line.opacity = 0
                self.__highlight_marker.opacity = 1
            else:
                self.__highlight_line.opacity = 1
                self.__highlight_marker.opacity = 0
                self.__highlight_line.pos1 = (self.__highlight_pixel, self.__highlight_line.pos1[1])
                self.__highlight_line.pos2 = (self.__highlight_pixel, self.__highlight_line.pos2[1])

        else:
            self.__vis_params.highlight_time = self.__calculate_time_from_pixel(self.__highlight_line.pos1[0])

    def __show_interval_slider(self, event=None):
        """
        Called when mouse hovers over TimeAxisNodeDiv. Shows Details on demand of interval.
        """
        # make interval rect bigger
        self.__i_rect.size = (self.__i_rect.size[0], 13)
        # show label with current total interval time
        self.__i_label.opacity = 1
        # show interval scrollbar
        self.__i_scrollbar.opacity = 1

    def __hide_interval_slider(self, event=None):
        """
        Hide Details on Demand of interval when mouse hovers out of TimeAxisNodeDiv area.
        """
        # make interval rect normal size again
        self.__i_rect.size = (self.__i_rect.size[0], 5)
        # hide label with current total interval time
        self.__i_label.opacity = 0
        # hide interval scrollbar
        self.__i_scrollbar.opacity = 0

    def __on_visualization_hover_over(self, event=None):
        # TODO: Move to view
        """
        Moves the highlight line along the vertical mouse position.
        """
        rel_pos = self.getRelPos(event.pos)
        self.__highlight_line.pos1 = (rel_pos[0], self.__highlight_line.pos1[1])
        self.__highlight_line.pos2 = (rel_pos[0], self.__highlight_line.pos2[1])
        # let line appear in front of every other child in this div
        self.removeChild(self.__highlight_line)
        self.appendChild(self.__highlight_line)
        self.__vis_params.notify()

    def __show_highlight_line(self, event=None):
        """
        Shows highlight line when mouse hovers over visualization.
        """
        if self.__pinned:
            if not self.__highlight_pixel > self.width and not self.__highlight_pixel < 0:
                self.__highlight_line.opacity = 1
        else:
            self.__highlight_line.opacity = 1

    def __hide_highlight_line(self, event=None):
        """
        Hides highlight line when mouse exits area of visualization.
        """
        if not self.__pinned:
            self.__highlight_line.opacity = 0

    def __toggle_pin_highlight_line(self, event=None):
        """
        Allows the highlight line to be pinned at the current mouse location.
        """
        # unpin line
        if self.__pinned:
            self.__highlight_line.color = global_values.COLOR_SECONDARY
            rel_pos = self.getRelPos(event.pos)
            self.__highlight_line.pos1 = (rel_pos[0], self.__highlight_line.pos1[1])
            self.__highlight_line.pos2 = (rel_pos[0], self.__highlight_line.pos2[1])
            self.__highlight_line.opacity = 1
            self.__highlight_marker.opacity = 0
            self.__hover_id = self.parent.data_div.subscribe(avg.Node.CURSOR_MOTION, self.__on_visualization_hover_over)
            self.__pinned = False
        # pin line
        else:
            self.__vis_params.highlight_time = self.__calculate_time_from_pixel(self.__highlight_line.pos1[0])
            marker_pos = self._value_to_pixel(self.__vis_params.highlight_time,
                                              self.data_range[0], self.data_range[1])
            self.__highlight_marker.pos1 = (marker_pos, self.__highlight_marker.pos1[1])
            self.__highlight_marker.pos2 = (marker_pos, self.__highlight_marker.pos2[1])
            self.__highlight_marker.opacity = 1
            self.__highlight_line.color = global_values.COLOR_WHITE
            self.parent.data_div.unsubscribe(avg.Node.CURSOR_MOTION, self.__hover_id)
            self.__pinned = True
            self.__vis_params.notify()

    def __calculate_time_from_pixel(self, pixel):
        """
        Calculates the time in milliseconds of the given pixel value within the width of the axis.
        :param pixel the pixel value to be converted to time in ms
        """
        time_i_range = self.end - self.start            # time
        ratio = pixel / self.width                      # %
        time = ratio * time_i_range + self.start        # time
        return time


"""utils"""


def r_pretty(dmin, dmax, n, time=False):
    """
    Calculates "nice" ticks for axis (R's pretty algorithm).
    :param dmin: minimum data value
    :param dmax: maximum data value
    :param n: number of desired ticks
    :param time: bool, True: handles tick calculation different for time values
    :return: list with tick values
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
