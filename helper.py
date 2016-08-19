#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
