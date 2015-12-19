import colorsys
import database

colors_hsv = [[35 / float(360), 0.41, 1], [0, 0.50, 1], [287 / float(360), 0.34, 1], [205 / float(360), 0.33, 1]]
samples_per_pixel = 0.3
averaging_count = 500
start_time = 0
end_time = database.max_time
zoom_strength = 0.1


def zoom_in_at(percentage_in_timeframe):
    global start_time, end_time
    point = start_time + percentage_in_timeframe * (end_time - start_time)
    start_time = point - (point - start_time) * (1 - zoom_strength)
    end_time = point + (end_time - point) * (1 - zoom_strength)


def zoom_out_at(percentage_in_timeframe):
    global start_time, end_time

    point = start_time + percentage_in_timeframe * (end_time - start_time)
    start_time -= (point - start_time) * 1 / ((1 / zoom_strength) - 1)
    end_time += (end_time - point) * 1 / ((1 / zoom_strength) - 1)

    if start_time < database.min_time:
        start_time = database.min_time

    if end_time > database.max_time:
        end_time = database.max_time


def shift_time(forwards):
    global end_time, start_time
    if forwards:
        shift_amount = end_time - start_time * zoom_strength
    else:
        shift_amount = -(end_time - start_time * zoom_strength)
    if start_time + shift_amount < database.min_time:
        shift_amount = database.min_time - start_time
    if end_time + shift_amount > database.max_time:
        shift_amount = database.max_time - end_time

    start_time += shift_amount
    end_time += shift_amount


def getColorAsHex(index, opacity):
    if index < 0 or index > 3:
        index = 0
        print "color index out of range"
    hsv = colors_hsv[index]
    hsv = colorsys.hsv_to_rgb(hsv[0], min(1, hsv[1] * opacity * opacity * opacity * opacity * 4), hsv[2])
    color = (int(hsv[0] * 255), int(hsv[1] * 255), int(hsv[2] * 255))
    color = '%02x%02x%02x' % color
    return color
