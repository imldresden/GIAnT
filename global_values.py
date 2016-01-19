import colorsys

colors_hsv = [[35 / float(360), 0.41, 1], [0, 0.50, 1], [287 / float(360), 0.34, 1], [205 / float(360), 0.33, 1]]
samples_per_pixel = 0.2
averaging_count = 500

def get_color_as_hex(index, opacity):
    if index < 0 or index > 3:
        index = 0
        print "color index out of range"
    hsv = colors_hsv[index]
    hsv = colorsys.hsv_to_rgb(hsv[0], min(1, hsv[1] * opacity * opacity * opacity * opacity * 4), hsv[2])
    color = (int(hsv[0] * 255), int(hsv[1] * 255), int(hsv[2] * 255))
    color = '%02x%02x%02x' % color
    return color
