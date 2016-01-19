import colorsys
import database
import time

colors_hsv = [[35 / float(360), 0.41, 1], [0, 0.50, 1], [287 / float(360), 0.34, 1], [205 / float(360), 0.33, 1]]
samples_per_pixel = 0.2
averaging_count = 500
total_range = [database.min_time, database.max_time]
x_range = [database.min_x, database.max_x]
__interval_range = [total_range[0], total_range[1]]
__interval_range_last = [total_range[0], total_range[1]]
interval_range_target = [total_range[0], total_range[1]]    # temporary global
animation_start_time = -1                                   # temporary global
__animation_duration = 1
__zoom_strength = 0.1


# updates the current interval to the interpolated value for the animation
def update_interval_range():
    global animation_start_time, __animation_duration, interval_range_target, __interval_range, __interval_range_last
    if animation_start_time == -1:
        return False

    progress = (time.time() - animation_start_time) / __animation_duration
    if progress >= 1:
        __interval_range = list(interval_range_target)

        animation_start_time = -1
        return True
    __interval_range[0] = progress * interval_range_target[0] + (1 - progress) * __interval_range_last[0]
    __interval_range[1] = progress * interval_range_target[1] + (1 - progress) * __interval_range_last[1]
    return True


# gets the interval for the current animation step
def get_interval_range():
    global __interval_range
    update_interval_range()
    return __interval_range


# zooms in around the mouse (sets the target interval, which is later animated using update_interval_range())
def zoom_in_at(fraction_in_timeframe):
    global __interval_range, animation_start_time, __interval_range_last, interval_range_target
    __interval_range_last = list(__interval_range)
    animation_start_time = time.time()
    update_interval_range()

    point = interval_range_target[0] + fraction_in_timeframe * (interval_range_target[1] - interval_range_target[0])
    interval_range_target[0] = point - (point - interval_range_target[0]) * (1 - __zoom_strength)
    interval_range_target[1] = point + (interval_range_target[1] - point) * (1 - __zoom_strength)

# zooms out around the mouse (sets the target interval, which is later animated using update_interval_range())
def zoom_out_at(fraction_in_timeframe):
    global __interval_range, total_range, animation_start_time, __interval_range_last, interval_range_target
    __interval_range_last = list(__interval_range)
    animation_start_time = time.time()
    update_interval_range()
    point = interval_range_target[0] + fraction_in_timeframe * (interval_range_target[1] - interval_range_target[0])
    interval_range_target[0] -= (point - interval_range_target[0]) * 1 / ((1 / __zoom_strength) - 1)
    interval_range_target[1] += (interval_range_target[1] - point) * 1 / ((1 / __zoom_strength) - 1)

    if interval_range_target[0] < total_range[0]:
        interval_range_target[0] = total_range[0]

    if interval_range_target[1] > total_range[1]:
        interval_range_target[1] = total_range[1]


# shifts the interval (sets the target interval, which is later animated using update_interval_range())
def shift_time(forwards):
    global __interval_range, total_range, animation_start_time, __interval_range_last
    __interval_range_last = list(__interval_range)
    animation_start_time = time.time()
    update_interval_range()
    if forwards:
        shift_amount = (interval_range_target[1] - interval_range_target[0]) * __zoom_strength
    else:
        shift_amount = -(interval_range_target[1] - interval_range_target[0]) * __zoom_strength
    if interval_range_target[0] + shift_amount < total_range[0]:
        shift_amount = total_range[0] - interval_range_target[0]
    if interval_range_target[1] + shift_amount > total_range[1]:
        shift_amount = total_range[1] - interval_range_target[1]

    interval_range_target[0] += shift_amount
    interval_range_target[1] += shift_amount


def getColorAsHex(index, opacity):
    if index < 0 or index > 3:
        index = 0
        print "color index out of range"
    hsv = colors_hsv[index]
    hsv = colorsys.hsv_to_rgb(hsv[0], min(1, hsv[1] * opacity * opacity * opacity * opacity * 4), hsv[2])
    color = (int(hsv[0] * 255), int(hsv[1] * 255), int(hsv[2] * 255))
    color = '%02x%02x%02x' % color
    return color
