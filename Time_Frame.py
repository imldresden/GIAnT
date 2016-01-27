import time
import database

total_range = [database.min_time, database.max_time]


class time_frame:
    __interval_range = [total_range[0], total_range[1]]
    __interval_range_last = [total_range[0], total_range[1]]
    __interval_range_target = [total_range[0], total_range[1]]
    __highlight_time = 0
    __animation_start_time = -1
    __animation_duration = 1
    __zoom_strength = 0.1

    __subscribers = []

    # updates the current interval to the interpolated value for the animation
    def update_interval_range(self):
        if self.__animation_start_time == -1:
            return False

        progress = (time.time() - self.__animation_start_time) / self.__animation_duration
        if progress >= 1:
            self.__interval_range = list(self.__interval_range_target)

            self.__animation_start_time = -1
            self.publish()
            return True

        new_range = [0, 0]
        new_range[0] = progress * self.__interval_range_target[0] + (1 - progress) * self.__interval_range_last[0]
        new_range[1] = progress * self.__interval_range_target[1] + (1 - progress) * self.__interval_range_last[1]

        if new_range != self.__interval_range:
            self.__interval_range = new_range
            self.publish()
        return True

    # gets the interval for the current animation step
    def get_interval_range(self):
        self.update_interval_range()
        return self.__interval_range

    # zooms in around the mouse (sets the target interval, which is later animated using update_interval_range())
    def zoom_in_at(self, fraction_in_timeframe):
        self.__interval_range_last = list(self.__interval_range)
        self.__animation_start_time = time.time()
        self.update_interval_range()

        point = self.__interval_range_target[0] + fraction_in_timeframe * (self.__interval_range_target[1] - self.__interval_range_target[0])
        self.__interval_range_target[0] = point - (point - self.__interval_range_target[0]) * (1 - self.__zoom_strength)
        self.__interval_range_target[1] = point + (self.__interval_range_target[1] - point) * (1 - self.__zoom_strength)

    # zooms out around the mouse (sets the target interval, which is later animated using update_interval_range())
    def zoom_out_at(self, fraction_in_timeframe):
        self.__interval_range_last = list(self.__interval_range)
        self.__animation_start_time = time.time()
        self.update_interval_range()
        point = self.__interval_range_target[0] + fraction_in_timeframe * (self.__interval_range_target[1] - self.__interval_range_target[0])
        self.__interval_range_target[0] -= (point - self.__interval_range_target[0]) * 1 / ((1 / self.__zoom_strength) - 1)
        self.__interval_range_target[1] += (self.__interval_range_target[1] - point) * 1 / ((1 / self.__zoom_strength) - 1)

        if self.__interval_range_target[0] < total_range[0]:
            self.__interval_range_target[0] = total_range[0]

        if self.__interval_range_target[1] > total_range[1]:
            self.__interval_range_target[1] = total_range[1]

    # shifts the interval (sets the target interval, which is later animated using update_interval_range())
    def shift_time(self, forwards):
        self.__interval_range_last = list(self.__interval_range)
        self.__animation_start_time = time.time()
        self.update_interval_range()
        if forwards:
            shift_amount = (self.__interval_range_target[1] - self.__interval_range_target[0]) * self.__zoom_strength
        else:
            shift_amount = -(self.__interval_range_target[1] - self.__interval_range_target[0]) * self.__zoom_strength
        if self.__interval_range_target[0] + shift_amount < total_range[0]:
            shift_amount = total_range[0] - self.__interval_range_target[0]
        if self.__interval_range_target[1] + shift_amount > total_range[1]:
            shift_amount = total_range[1] - self.__interval_range_target[1]

        self.__interval_range_target[0] += shift_amount
        self.__interval_range_target[1] += shift_amount

    def set_time_frame(self, interval):
        self.__interval_range_last = list(interval)
        self.__interval_range_target = list(interval)
        self.__interval_range = list(interval)
        self.publish()

    def subscribe(self, target):
        self.__subscribers.append(target)

    def publish(self):
        for subscriber in self.__subscribers:
            subscriber.update_time_frame(self.__interval_range)

    def __set_highlight_time(self, time):
        self.__highlight_time = time

    def __get_highlight_time(self):
        return self.__highlight_time

    highlight_time = property(__get_highlight_time, __set_highlight_time)

main_time_frame = time_frame()
