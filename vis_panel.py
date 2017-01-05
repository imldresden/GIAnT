# -*- coding: utf-8 -*-
# GIAnT Group Interaction Analysis Toolkit
# Copyright (C) 2017 Interactive Media Lab Dresden
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

import libavg
from libavg import avg

import global_values
import helper


class VisPanel(avg.DivNode):

    def __init__(self, label, vis_params, axis_size, show_grid, aspect=None, parent=None, **kwargs):
        super(VisPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.crop = True

        self.__axis_size = avg.Point2D(axis_size)
        data_div_size = self.size - self.__axis_size
        if aspect is not None:
            data_div_size.y = data_div_size.x * aspect
            self.size = data_div_size + self.__axis_size

        # rect for background
        avg.RectNode(pos=(self.__axis_size.x, 0), size=data_div_size,
                strokewidth=0, fillopacity=1, fillcolor=global_values.COLOR_BLACK, parent=self)
        self._grid_div = avg.DivNode(pos=(self.__axis_size.x, 0), size=data_div_size, parent=self)
        # rect for border
        avg.RectNode(pos=(self.__axis_size.x, 0), size=data_div_size,
                strokewidth=1, color=global_values.COLOR_FOREGROUND, parent=self)

        self._data_div = avg.DivNode(pos=(self.__axis_size.x, 0), size=data_div_size, crop=True)

        avg.WordsNode(pos=(10, 8), color=global_values.COLOR_FOREGROUND, text=label, sensitive=False,
                fontsize=global_values.FONT_SIZE, parent=self._data_div)

        vis_params.subscribe(vis_params.CHANGED, self._update_time)
        self._vis_params = vis_params

        self.__show_grid = show_grid
        self._x_grid = []
        self._y_grid = []

        self._x_axis = None
        self._y_axis = None

    def _create_x_axis(self, top_axis=False, **kwargs):
        if top_axis:
            pos = (self.__axis_size.x, 0)
        else:
            pos = (self.__axis_size.x, self._data_div.height)
        self._x_axis = AxisNode(pos=pos, size=(self._data_div.width, self.__axis_size.y),
                top_axis=top_axis, parent=self, **kwargs)

    def _create_y_axis(self, **kwargs):
        self._y_axis = AxisNode(pos=(0, 0), size=(self.__axis_size.x, self._data_div.height),
                parent=self, **kwargs)

    def _create_data_div(self):
        self.appendChild(self._data_div)
        if self.__show_grid:
            self._update_grid()

    def _update_grid(self):
        # Horizontal
        helper.unlink_node_list(self._x_grid)
        self._x_grid = []

        if self._x_axis:
            tick_posns = self._x_axis.get_tick_posns()
            y_max = self._data_div.height
            for x in tick_posns:
                node = avg.LineNode(pos1=(x, 0), pos2=(x, y_max), color=global_values.COLOR_BACKGROUND,
                        parent=self._grid_div)
                self._x_grid.append(node)

        # Vertical
        helper.unlink_node_list(self._y_grid)
        self._y_grid = []

        if self._y_axis:
            tick_posns = self._y_axis.get_tick_posns()
            x_max = self._data_div.width
            for y in tick_posns:
                node = avg.LineNode(pos1=(0, y), pos2=(x_max, y), color=global_values.COLOR_BACKGROUND,
                    parent=self._grid_div)
                self._y_grid.append(node)


class AxisNode(avg.DivNode):

    TICK_LENGTH = 10

    def __init__(self, data_range, unit="m", hide_rims=False, top_axis=False, inverted=False, parent=None,
                 label_offset=0, tick_positions=None, **kwargs):
        """
        Custom AxisNode with axis lines, grid lines and labeling.
        :param data_range: The minimum and maximum data range to be displayed
        :param unit: Unit of measurement (time: ms, length: cm)
        :param hide_rims: Hides first tick if True
        :param top_axis: Determines if a slimmed x-axis should be displayed at the top instead of the bottom
        :param inverted: If True, values on axis are displayed inverted
        """
        super(AxisNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        """attributes"""
        self.__parent = parent
        self.__top_axis = top_axis                           # determines if the x-axis should be displayed at the top
        self.__label_offset = label_offset                   # offset of tick labels from axis line
        if tick_positions is None:
            self.__tick_positions = []                       # contains the data values of the tick labels
            self.__auto_tick_positions = True
        else:
            self.__tick_positions = tick_positions
            self.__auto_tick_positions = False
        self.__label_pos = []                                # contains the pos at axis for each label in __label_values
        self.__ticks = []                                    # separation lines (ticks) for axis
        self.__label_nodes = []                              # WordNodes for tick labels with values from _labels
        self.__vertical = False                              # if True, axis is drawn vertically
        self.__data_range = data_range                       # data range of data set
        self.__unit = unit                                   # unit of measurement
        self.__hide_rims = hide_rims                         # determines if the first and last tick are shown
        self.__inverted = inverted                           # shows values on axis inverted if true

        # axis is displayed vertical if width smaller than height
        if self.height > self.width:
            self.__vertical = True

        # initial update
        self.update(data_range[0], data_range[1])

    def update(self, start, end):
        """
        updates position of ticks and labels, and value of labels
        needs to be called whenever corresponding data is changing (e.g. in onFrame())
        :param start: start value in unit of measurement (not in pixel)
        :param end: end value in unit of measurement (not in pixel)
        """
        self.__data_range = [start, end]

        if self.__auto_tick_positions:
            # calculate tick marks with R's pretty algorithm and format numbers
            is_time = (self.__unit is "s")
            self.__tick_positions = r_pretty(dmin=start, dmax=end, n=5, time=is_time)
            # delete first and last tick except it is min or max of data range
            self.__tick_positions.pop(len(self.__tick_positions) - 1)
            if self.__hide_rims:
                self.__tick_positions.pop(0)

        # calculate positions of ticks within AxisNode
        if self.__inverted:
            offset = self.value_to_pixel(end)
        else:
            offset = self.value_to_pixel(start)
        self.__label_pos = [self.value_to_pixel(t) - offset for t in self.__tick_positions]

        self.__draw_ticks()

    def __draw_ticks(self):
        """
        draw each tick and the corresponding tick label on the position at the axis line
        """
        helper.unlink_node_list(self.__ticks)
        self.__ticks = [None] * len(self.__label_pos)

        # delete old axis labels
        helper.unlink_node_list(self.__label_nodes)
        self.__label_nodes = [None] * len(self.__label_pos)

        # for each tick create new tick-line, value label and grid line at position on axis line
        for i, pos in enumerate(self.__label_pos):
            # create new axis tick, label and grid line
            tick = libavg.LineNode(strokewidth=1, color=global_values.COLOR_FOREGROUND, parent=self)
            self.__ticks[i] = tick
            self.__label_nodes[i] = libavg.WordsNode(color=global_values.COLOR_FOREGROUND,
                    fontsize=global_values.FONT_SIZE, parent=self)

            # set label value
            if not self.__top_axis:
                self.__label_nodes[i].text = self.__format_label(self.__tick_positions[i])
            label = self.__label_nodes[i]

            if self.__vertical:
                v_center = label.fontsize / 2
                tick.pos1 = (self.width, pos)
                tick.pos2 = (self.width + self.TICK_LENGTH, pos)
                label.alignment = "right"
                label.pos = (self.width - self.TICK_LENGTH - self.__label_offset, pos - v_center - 1)
            else:
                tick.pos2 = (pos, 0)
                if self.__top_axis:
                    tick.pos1 = (pos, self.TICK_LENGTH)
                else:
                    tick.pos1 = (pos, - self.TICK_LENGTH)
                label.pos = (pos, self.TICK_LENGTH/2 + self.__label_offset)
                label.alignment = "center"

    def get_tick_posns(self):
        if self.__vertical:
            return [tick.pos1.y for tick in self.__ticks]
        else:
            return [tick.pos1.x for tick in self.__ticks]

    def value_to_pixel(self, value, start=None, end=None):
        if start is None:
            start = self.__data_range[0]
        if end is None:
            end = self.__data_range[1]

        if self.__vertical:
            length = self.height
        else:
            length = self.width

        a = (end - start) / length
        pixel_pos = (value - start) / a

        if self.__inverted:
            return length - pixel_pos
        else:
            return pixel_pos

    def get_hide_rims(self):
        return self.__hide_rims

    def set_hide_rims(self, hide_rims):
        self.__hide_rims = hide_rims
    hide_rims = property(get_hide_rims, set_hide_rims)

    def __format_label(self, value):
        if self.__unit is "m":  # meters
            # cut zeros if value is integer
            if value % 1 in (0, 0.0):
                value = int(value)
            else:
                value = round(value, 4)

            return "{} m".format(value)

        elif self.__unit is "s":  # seconds
            return helper.format_time(value)

        elif self.__unit is "px": # pixels
            return ""

        assert False


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

    graphmin = ns * unit
    graphmax = nu * unit
    count = int(math.ceil(graphmax - graphmin) / unit)
    res = [graphmin + k * unit for k in range(count + 1)]
    if res[0] < dmin:
        res[0] = dmin
    if res[-1] > dmax:
        res[-1] = dmax
    return res
