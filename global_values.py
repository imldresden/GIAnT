import database

"""visualization values"""
samples_per_pixel = 0.1
averaging_count = 500                               # smoothness of curves in visualization
default_averaging_count = averaging_count           # default value of smoothness
time_step_size = 50                                 # time in ms over witch data is averaged from database

"""data values"""
wall_width = 490                                    # width of display wall in cm
wall_height = 206                                   # height of display wall in cm
x_range = [database.min_x, database.max_x]          # data range of wall width from right (min) to left (max)
y_range = [database.min_y, database.max_y]          # data range of wall height from bottom (min) to top (max)
z_range = [database.min_z, database.max_z]          # data range of room depth from front (min) to back (max)
x_touch_range = [0, 4*1920]
y_touch_range = [0, 3*1080]
x_wall_range = [0, wall_width]
y_wall_range = [40, 40+wall_height]

"""color values"""
user_color_schemes = [                              # different user color schemes
    [[ 35 / float(360), 0.409, 1],                  # Yellow
    [  0 / float(360), 0.500, 1],                   # Red
    [286 / float(360), 0.567, 1],                   # Purple
    [152 / float(360), 0.568, 1]],                  # Green

    [[  0 / float(360), 0.29, 1],                   # Red
    [ 27 / float(360), 0.29, 1],                    # Brownish
    [180 / float(360), 0.18, 1],                    # Blue
    [120 / float(360), 0.23, 1]]                    # Green
]
COLOR_FOREGROUND = "BBBBBB"                         # foreground color used for axis and text
COLOR_SECONDARY = "888888"                          # second more faint foreground color
COLOR_BACKGROUND = "222222"                         # background color
COLOR_HIGHLIGHT = "FF0000"                          # distinctive highlight color
COLOR_BLACK = "010101"                              # for black background
COLOR_WHITE = "FFFFFF"                              # for bright highlights
COLOR_DARK_GREY = "636363"                          # used for cosmetics

"""display values"""
APP_MARGIN = 15                                     # space of content to application window in px
APP_PADDING = 10                                    # space between content of application in px
