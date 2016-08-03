# -*- coding: utf-8 -*-

import pat_model
import vis_panel
from libavg import avg, player

player.loadPlugin("vwline")


class WallPanel(vis_panel.VisPanel):

    PIXELS_PER_SAMPLE = 4
    MAX_SMOOTHNESS = 500

    def __init__(self, session, vis_params, parent, **kwargs):
        super(WallPanel, self).__init__("Wall", vis_params, (60, 25), parent, **kwargs)

        self.__users = session.users

        self._create_y_axis(data_range=pat_model.x_touch_range, unit="px", hide_rims=True)
        self._create_x_axis(data_range=pat_model.y_touch_range, unit="px")

        self._create_data_div()

    def _update_time(self, vis_params):
        interval = vis_params.get_time_interval()
