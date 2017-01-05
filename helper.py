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

def unlink_node_list(node_list):
    for node in node_list:
        node.unlink(True)


def format_time(value, show_ms=True):
    ms = int((value - int(value)) * 1000 + 0.5)
    m, s = divmod(value, 60)
    time_str = "{:02d}:{:02d}".format(int(m), int(s))
    if show_ms and ms != 0:
        time_str += ".{:03d}".format(ms)
    return time_str
