# -*- coding: utf-8 -*-

import vis_panel

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
        self.__data_div = avg.DivNode(pos=(X_MARGIN, 0), parent=self)

        avg.WordsNode(pos=(0, 25 + LINE_SPACING*2), text="Distance travelled: ", parent=self.__data_div)
        self.__dist_nodes = []
        avg.WordsNode(pos=(0, 25 + LINE_SPACING*3), text="Avg. dist from wall: ", parent=self.__data_div)
        self.__avg_dist_nodes = []
        avg.WordsNode(pos=(0, 25 + LINE_SPACING*4), text="Number of touches: ", parent=self.__data_div)
        self.__num_touches_nodes = []
        for col in range(4):
            col_x = COL_MARGIN+COL_WIDTH*col
            avg.WordsNode(pos=(col_x, 25 + LINE_SPACING), text="User "+str(col+1),
                    color=vis_params.get_user_color(col), parent=self.__data_div)
            dist_node = avg.WordsNode(pos=(col_x, 25+LINE_SPACING*2), parent=self.__data_div)
            self.__dist_nodes.append(dist_node)
            avg_dist_node = avg.WordsNode(pos=(col_x, 25 + LINE_SPACING * 3), parent=self.__data_div)
            self.__avg_dist_nodes.append(avg_dist_node)
            num_touches_node = avg.WordsNode(pos=(col_x, 25 + LINE_SPACING * 4), parent=self.__data_div)
            self.__num_touches_nodes.append(num_touches_node)

        vis_params.subscribe(vis_params.CHANGED, self.__update)

    def __update(self, vis_params):
        start_time = vis_params.get_time_interval()[0]
        end_time = vis_params.get_time_interval()[1]

        for i, user in enumerate(self.__session.users):
            self.__dist_nodes[i].text = "{:.2f}".format(user.getDistTravelled(start_time, end_time))+" m"
            self.__avg_dist_nodes[i].text = "{:.2f}".format(user.getAvgDistFromWall(start_time, end_time))+" m"
            self.__num_touches_nodes[i].text = str(len(user.getTouches(start_time, end_time)))
