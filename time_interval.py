# -*- coding: utf-8 -*-

import time
import database
import global_values
import util
from libavg import avg

total_range = [database.min_time, database.max_time]
total_range_value = total_range[1] - total_range[0]


class TimeInterval(avg.Publisher):
    CHANGED = avg.Publisher.genMessageID()

    __interval_range = list(total_range)

    __highlight_time = 0
    __animation_start_time = -1
    __animation_duration = 1
    __zoom_strength = 0.1

    def __init__(self):
        super(TimeInterval, self).__init__()
        self.__play = False
        self.__last_frame_time = time.time()
        self.publish(TimeInterval.CHANGED)

    def get_interval_range(self):
        return self.__interval_range

    def zoom_in_at(self, fraction_in_timeframe):
        point = self.__interval_range[0] + fraction_in_timeframe * (self.__interval_range[1] - self.__interval_range[0])
        self.__interval_range[0] = point - (point - self.__interval_range[0]) * (1 - self.__zoom_strength)
        self.__interval_range[1] = point + (self.__interval_range[1] - point) * (1 - self.__zoom_strength)
        self.notify()

    def zoom_out_at(self, fraction_in_timeframe):
        if self.__interval_range == total_range:
            return
        point = self.__interval_range[0] + fraction_in_timeframe * (self.__interval_range[1] - self.__interval_range[0])
        self.__interval_range[0] -= (point - self.__interval_range[0]) * 1 / ((1 / self.__zoom_strength) - 1)
        self.__interval_range[1] += (self.__interval_range[1] - point) * 1 / ((1 / self.__zoom_strength) - 1)

        if self.__interval_range[0] < total_range[0]:
            self.__interval_range[0] = total_range[0]

        if self.__interval_range[1] > total_range[1]:
            self.__interval_range[1] = total_range[1]
        self.notify()

    def shift_time(self, forwards, amount=-1):
        if amount == -1:
            if forwards:
                shift_amount = (self.__interval_range[1] - self.__interval_range[0]) * self.__zoom_strength
            else:
                shift_amount = -(self.__interval_range[1] - self.__interval_range[0]) * self.__zoom_strength
        else:
            if forwards:
                shift_amount = amount
                if self.__interval_range[1] + shift_amount > total_range[1]:
                    shift_amount = total_range[1] - self.__interval_range[1]
            else:
                shift_amount = -amount
                if self.__interval_range[0] + shift_amount < total_range[0]:
                    shift_amount = total_range[0] - self.__interval_range[0]

            self.__interval_range[0] += shift_amount
            self.__interval_range[1] += shift_amount
            self.notify()
            return

        if self.__interval_range[0] + shift_amount < total_range[0]:
            shift_amount = total_range[0] - self.__interval_range[0]
        if self.__interval_range[1] + shift_amount > total_range[1]:
            shift_amount = total_range[1] - self.__interval_range[1]

        self.__interval_range[0] += shift_amount
        self.__interval_range[1] += shift_amount

    def set_time_frame(self, interval):
        self.__interval_range = list(interval)
        self.notify()

    def notify(self, draw_lines=True):
        if global_values.link_smoothness:
            i_range = self.__interval_range[1] - self.__interval_range[0]
            s = i_range * (global_values.max_averaging_count - global_values.min_averaging_count) / total_range_value
            util.change_smoothness(s)
        self.notifySubscribers(TimeInterval.CHANGED, [self.__interval_range, draw_lines])

    def play_animation(self):
        self.__play = not self.__play
        self.__last_frame_time = time.time()

    def __set_highlight_time(self, time):
        self.__highlight_time = time

    def __get_highlight_time(self):
        return self.__highlight_time
    highlight_time = property(__get_highlight_time, __set_highlight_time)

    def __get_play(self):
        return self.__play
    play = property(__get_play)

    def __set_last_frame_time(self, t):
        self.__last_frame_time = t

    def __get_last_frame_time(self):
        return self.__last_frame_time
    last_frame_time = property(__get_last_frame_time, __set_last_frame_time)


main_time_frame = TimeInterval()
