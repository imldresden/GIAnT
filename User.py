# -*- coding: utf-8 -*-

import database

users = []


class User:
    def __init__(self, index):
        self.index = index - 1

        self.head_positions_integral = database.get_head_positions_integral(index)
        self.head_orientations = database.get_head_orientations(index)

        self.viewpoints_integral = database.get_view_points_integral(index)

        self.touches = database.get_touch_positions(index)
        self.selected = True

        users.append(self)

    def get_head_position_averaged(self, index, smoothness):
        count = min(smoothness, len(self.head_positions_integral) - index - 1)
        integral = self.head_positions_integral
        if count <= 0:
            count = 1
        index = min(max(0, index), len(integral) - count - 1)

        head_position = [(integral[index + count][0] - integral[index][0]) / count,
                         (integral[index + count][1] - integral[index][1]) / count,
                         (integral[index + count][2] - integral[index][2]) / count,
                         integral[index + count][3]]
        return head_position

    def get_head_orientation(self, index):
        head_orientation = self.head_orientations[index]
        return head_orientation

    def get_view_point_averaged(self, index, smoothness):
        # TODO: Unused, untested
        count = min(smoothness, len(self.viewpoints_integral) - index - 1)
        integral = self.viewpoints_integral
        if count <= 0:
            count = 1
        index = min(max(0, index), len(integral) - count - 1)

        view_point = [(integral[index + count][0] - integral[index][0]) / count,
                      (integral[index + count][1] - integral[index][1]) / count,
                      integral[index + count][2]]
        return view_point


for userid in range(1, 5):
            User(userid)
