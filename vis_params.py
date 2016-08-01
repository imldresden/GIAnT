# -*- coding: utf-8 -*-

import time
from libavg import avg


class VisParams(avg.Publisher):
    CHANGED = avg.Publisher.genMessageID()

    MIN_SMOOTHNESS_FACTOR = 0.01
    MAX_SMOOTHNESS_FACTOR = 1

    __highlight_time = 0
    __zoom_strength = 0.1

    def __init__(self, session):
        super(VisParams, self).__init__()
        self.__play = False
        self.__last_frame_time = time.time()
        self.__time_interval = [0, session.duration]
        self.publish(VisParams.CHANGED)

        self.__smoothness_factor = 1
        self.__users_visible = [True]*session.num_users
        self.__duration = session.duration

    def get_time_interval(self):
        return self.__time_interval

    def zoom_in_at(self, fraction_in_timeframe):
        point = self.__time_interval[0] + fraction_in_timeframe * (self.__time_interval[1] - self.__time_interval[0])
        self.__time_interval[0] = point - (point - self.__time_interval[0]) * (1 - self.__zoom_strength)
        self.__time_interval[1] = point + (self.__time_interval[1] - point) * (1 - self.__zoom_strength)
        self.notify()

    def zoom_out_at(self, fraction_in_timeframe):
        time_range = [0, self.__duration]
        if self.__time_interval == time_range:
            return
        point = self.__time_interval[0] + fraction_in_timeframe * (self.__time_interval[1] - self.__time_interval[0])
        self.__time_interval[0] -= (point - self.__time_interval[0]) / ((1 / self.__zoom_strength) - 1)
        self.__time_interval[1] += (self.__time_interval[1] - point) / ((1 / self.__zoom_strength) - 1)

        if self.__time_interval[0] < time_range[0]:
            self.__time_interval[0] = time_range[0]

        if self.__time_interval[1] > time_range[1]:
            self.__time_interval[1] = time_range[1]
        self.notify()

    def shift_time(self, forwards, amount=-1):
        if amount == -1:
            amount = (self.__time_interval[1] - self.__time_interval[0]) * self.__zoom_strength
        if forwards:
            shift_amount = amount
        else:
            shift_amount = -amount

        if self.__time_interval[0] + shift_amount < 0:
            shift_amount = 0 - self.__time_interval[0]
        if self.__time_interval[1] + shift_amount > self.__duration:
            shift_amount = self.__duration - self.__time_interval[1]

        self.__time_interval[0] += shift_amount
        self.__time_interval[1] += shift_amount
        self.__highlight_time += shift_amount
        self.notify()

    def set_time_interval(self, interval):
        self.__time_interval = list(interval)
        self.notify()

    def notify(self):
        self.notifySubscribers(VisParams.CHANGED, [self])

    def play_animation(self):
        self.__play = not self.__play
        self.__last_frame_time = time.time()

    def get_user_visible(self, i):
        return self.__users_visible[i]

    def set_user_visible(self, i, visible):
        self.__users_visible[i] = visible
        self.notify()

    def set_smoothness_factor(self, value):
        self.__smoothness_factor = value

    def get_smoothness_factor(self):
        return self.__smoothness_factor

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

