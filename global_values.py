import database

samples_per_pixel = 0.05
averaging_count = 500
user_colors_hls = [[ 35 / float(360), 0.409, 1], # Yellow
                   [  0 / float(360), 0.500, 1], # Red
                   [286 / float(360), 0.567, 1], # Purple
                   [152 / float(360), 0.568, 1]] # Green
x_range = [database.min_x, database.max_x]
y_range = [database.min_y, database.max_y]
z_range = [database.min_z, database.max_z]
x_touch_range = [0, 4*1920]
y_touch_range = [0, 3*1080]
COLOR_FOREGROUND = "FFFFFF"
COLOR_SECONDARY = "333333"
COLOR_BACKGROUND = "000000"
COLOR_HIGHLIGHT = "FF0000"
