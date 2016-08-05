# -*- coding: utf-8 -*-

import math

import pat_model
import global_values
import vis_panel
import vis_params
from libavg import avg


class FloorPanel(vis_panel.VisPanel):

    def __init__(self, session, vis_params, parent, **kwargs):
        pos_range = pat_model.pos_range
        view_extent = avg.Point2D(pos_range[1][0] - pos_range[0][0], 3.0)
        aspect = view_extent.y/view_extent.x
        super(FloorPanel, self).__init__("Floor", vis_params, (60, 25), True, aspect, parent=parent, **kwargs)

        self.__users = session.users

        self._create_x_axis(data_range=(pos_range[0][0], pos_range[1][0]), unit="m", top_axis=True)
        self._create_y_axis(data_range=(-0.5,2.5), unit="m", hide_rims=True)
        self.__create_wall_rect()

        self._create_data_div()
        self.__user_nodes = []

    def _update_time(self, vis_params):
        self.__show_users(vis_params.highlight_time)

    def __show_users(self, time):
        self._unlink_node_list(self.__user_nodes)
        self.__user_nodes = []
        wall_y = self._y_axis.value_to_pixel(0)

        for i, user in enumerate(self.__users):
            pos = user.get_head_position(time)
            pixel_pos = avg.Point2D(self._x_axis.value_to_pixel(pos[0]), self._y_axis.value_to_pixel(pos[2]))
            rot = user.get_head_orientation(time)
            node = UserNode(user.userid, pos=pixel_pos, wall_y=wall_y, angle=rot[0], parent=self._data_div)
            self.__user_nodes.append(node)

    def __create_wall_rect(self):
        x_min = self._x_axis.value_to_pixel(0)
        x_max = self._x_axis.value_to_pixel(pat_model.wall_width)
        y_max = self._y_axis.value_to_pixel(0)

        avg.RectNode(pos=(x_min, y_max-16), size=(x_max - x_min, 16), fillcolor=global_values.COLOR_DARK_GREY,
                fillopacity=1, parent=self._data_div)


class UserNode(avg.DivNode):

    def __init__(self, userid, pos, wall_y, angle, parent, **kwargs):
        super(UserNode, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        color = vis_params.VisParams.get_user_color(userid)

        slope = math.tan(angle+math.pi/2)
        end_pos = avg.Point2D(pos.x + (pos.y - wall_y)/slope, wall_y)
        if (pos-end_pos).getNorm() > 200:
            end_pos = pos - avg.Point2D(math.sin(angle), math.cos(angle))*200
        avg.LineNode(pos1=pos, pos2=end_pos, color=color, parent=self)

        avg.CircleNode(pos=pos, r=6, fillopacity=1, color=color, fillcolor="000000", parent=self)
