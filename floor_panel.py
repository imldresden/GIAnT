# -*- coding: utf-8 -*-

import pat_model
import global_values
import vis_panel
from libavg import avg


class FloorPanel(vis_panel.VisPanel):

    def __init__(self, session, vis_params, parent, **kwargs):
        super(FloorPanel, self).__init__("Floor", vis_params, (60, 25), True, parent, **kwargs)

        self.__users = session.users

        pos_range = pat_model.pos_range
        self._create_x_axis(data_range=(pos_range[0][0], pos_range[1][0]), unit="m", top_axis=True)
        self._create_y_axis(data_range=(-0.5,2.5), unit="m", hide_rims=True)

        self._create_data_div()

    def _update_time(self, vis_params):
        self.__show_users(vis_params.highlight_time)

    def __show_users(self, time):
        for i, user in enumerate(self.__users):
            pass

