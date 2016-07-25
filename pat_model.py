# -*- coding: utf-8 -*-

import database

wall_width = 490
wall_height = 206
pos_range = [(0,0,50), (0,0,250)]  # User head position minimum and maximum
time_range = [0,0]
x_touch_range = [0, 4*1920]
y_touch_range = [0, 3*1080]
x_wall_range = [0, wall_width]
y_wall_range = [40, 40+wall_height]


class User:
    def __init__(self, index):
        self.index = index

        self.__head_positions_integral = database.get_head_positions_integral(index+1)
        self.__head_orientations = database.get_head_orientations(index+1)

        self.__viewpoints_integral = database.get_view_points_integral(index+1)

        self.__touches = database.get_touch_positions(index+1)

    def get_num_states(self):
        return len(self.__head_positions_integral)

    def get_head_position_averaged(self, cur_time, smoothness):
        count = smoothness
        integral = self.__head_positions_integral
        i = self.__time_to_index(cur_time)
        start_integral = integral[max(0, i - count/2)]
        end_integral = integral[min(len(integral)-1, i + (count+1)/2)]
        head_position = [(end_integral[0] - start_integral[0]) / count,
                         (end_integral[1] - start_integral[1]) / count,
                         (end_integral[2] - start_integral[2]) / count]
        return head_position

    def get_head_orientation(self, cur_time):
        i = self.__time_to_index(cur_time)
        head_orientation = self.__head_orientations[i]
        return head_orientation

    def get_view_point_averaged(self, cur_time, smoothness):
        # TODO: Unused, untested
        i = self.__time_to_index(cur_time)
        count = min(smoothness, len(self.__viewpoints_integral) - i - 1)
        integral = self.__viewpoints_integral
        if count <= 0:
            count = 1
        i = min(max(0, i), len(integral) - count - 1)

        view_point = [(integral[i + count][0] - integral[i][0]) / count,
                      (integral[i + count][1] - integral[i][1]) / count]
        return view_point

    def __time_to_index(self, t):
        return int(t * len(self.__head_positions_integral) / (time_range[1] - time_range[0]))
