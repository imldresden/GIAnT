import database

samples_per_pixel = 0.1
averaging_count = 500
user_colors_hls = [[ 35 / float(360), 0.409, 1], # Yellow
                   [  0 / float(360), 0.500, 1], # Red
                   [286 / float(360), 0.567, 1], # Purple
                   [152 / float(360), 0.568, 1]] # Green
x_range = [database.min_x, database.max_x]
COLOR_FOREGROUND = "FFFFFF"
COLOR_SECONDARY = "333333"
COLOR_BACKGROUND = "111111"
COLOR_HIGHLIGHT = "FF0000"
