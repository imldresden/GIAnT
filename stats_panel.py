# -*- coding: utf-8 -*-
import helper
import global_values

from libavg import avg, player

player.loadPlugin("heatmap")

X_MARGIN = 58
LINE_SPACING = 25
COL_WIDTH = 120
COL_MARGIN = 170

class StatsPanel(avg.DivNode):

    def __init__(self, session, vis_params, parent, **kwargs):
        super(StatsPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.__session = session
        colors = [vis_params.get_user_color(i) for i in range(4)]
        pos = avg.Point2D(50,0)
        self.__plot = ParallelCoordPlotNode(pos=pos, size=self.size-pos, obj_colors=colors,
                attrib_names = ["Dist travelled", "Avg. dist from wall", "Num Touches"],
                parent=self
        )
        vis_params.subscribe(vis_params.CHANGED, self.__update)


    def __update(self, vis_params):
        start_time = vis_params.get_time_interval()[0]
        end_time = vis_params.get_time_interval()[1]

        dist_travelled = []
        dist_from_wall = []
        num_touches = []
        for user in self.__session.users:
            dist_travelled.append(user.getDistTravelled(start_time, end_time))
            dist_from_wall.append(user.getAvgDistFromWall(start_time, end_time))
            num_touches.append(len(user.getTouches(start_time, end_time)))
        for i, attr in enumerate((dist_travelled, dist_from_wall, num_touches)):
            range = min(attr), max(attr)
            self.__plot.set_attr_vals(i, attr, range)

        self.__plot.update()


class ParallelCoordPlotAttrib:

    def __init__(self, name):
        self.name = name

        self.min = 0
        self.max = 0
        self.vals = []


class ParallelCoordPlotNode(avg.DivNode):

    MARGIN = (50,20)

    def __init__(self, obj_colors, attrib_names, parent, **kwargs):
        super(ParallelCoordPlotNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.__obj_colors = obj_colors
        self.__num_objs = len(obj_colors)
        self.__attribs = []
        for name in attrib_names:
            self.__attribs.append(ParallelCoordPlotAttrib(name))

        self.__axis_nodes = []
        self.__attrib_nodes = []

    def set_attr_vals(self, i, vals, range):
        assert (self.__num_objs == len(vals))
        self.__attribs[i].vals = vals
        self.__attribs[i].min = range[0]
        self.__attribs[i].max = range[1]

    def update(self):
        helper.unlink_node_list(self.__axis_nodes)
        self.__axis_nodes = []
        helper.unlink_node_list(self.__attrib_nodes)
        self.__attrib_nodes = []

        width_per_attr = (self.width - self.MARGIN[0] * 2) / (len(self.__attribs) - 1)
        axis_x_pos = [i*width_per_attr + self.MARGIN[0] for i in range(len(self.__attribs))]

        # axes
        for i in range(len(self.__attribs)):
            x_pos = axis_x_pos[i]
            axis_node = avg.DivNode(pos=(x_pos, 0), parent=self)
            avg.LineNode(pos1=(0,self.MARGIN[1]*2), pos2=(0,self.height-self.MARGIN[1]),
                    color=global_values.COLOR_FOREGROUND, parent=axis_node)

            attrib = self.__attribs[i]
            avg.WordsNode(pos=(0, 0), alignment="center", text=attrib.name, parent=axis_node)
            avg.WordsNode(pos=(0,self.MARGIN[1]), alignment="center", text=self.__format_label(attrib.min),
                    parent=axis_node)
            avg.WordsNode(pos=(0,self.height-self.MARGIN[1]), alignment="center", text=self.__format_label(attrib.max),
                    parent=axis_node)
            self.__axis_nodes.append(axis_node)

        axis_height = self.height - self.MARGIN[1]*3

        # Value polylines
        for i in range(self.__num_objs):
            color = self.__obj_colors[i]
            posns = []
            for j, attrib in enumerate(self.__attribs):
                val = float(attrib.vals[i])
                rel_y_pos = (val-attrib.min) / (attrib.max-attrib.min)
                y_pos = rel_y_pos * axis_height + self.MARGIN[1]*2
                posns.append((axis_x_pos[j], y_pos))
            polyline = avg.PolyLineNode(pos=posns, color=color, parent=self)
            self.__attrib_nodes.append(polyline)

    def __format_label(self, val):
        return "{}".format(round(val,2))
