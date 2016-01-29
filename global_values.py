import database

samples_per_pixel = 0.3
averaging_count = 500
time_step_size = 50

wall_width = 490
wall_height = 206

x_range = [database.min_x, database.max_x]
y_range = [database.min_y, database.max_y]
z_range = [database.min_z, database.max_z]
x_touch_range = [0, 4*1920]
y_touch_range = [0, 3*1080]
x_wall_range = [0, wall_width]
y_wall_range = [40, 40+wall_height]

user_colors_hls = [[ 35 / float(360), 0.409, 1],    # Yellow
                   [  0 / float(360), 0.500, 1],    # Red
                   [286 / float(360), 0.567, 1],    # Purple
                   [152 / float(360), 0.568, 1]]    # Green

COLOR_FOREGROUND = "FFFFFF"                         # foreground color used for axis and text
COLOR_SECONDARY = "333333"                          # second more faint foreground color
COLOR_BACKGROUND = "111111"                         # background color
COLOR_HIGHLIGHT = "FF0000"                          # distinctive highlight color
COLOR_BLACK = "000000"                              # for black background

APP_MARGIN = 15                                     # space of content to application window in px
APP_PADDING = 10                                    # space between content of application in px
