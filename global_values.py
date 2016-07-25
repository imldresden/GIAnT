# -*- coding: utf-8 -*-

"""visualization values"""
min_averaging_count = 1
max_averaging_count = 2000
link_smoothness = True                              # if the smoothness value should be linked to the current zoom level
default_smoothness = 500
time_step_size = 50                                 # time in ms over witch data is averaged from database

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

"""screen resolutions"""                            # common resolutions taken from
resolution = {                                      # http://www.w3schools.com/browsers/browsers_display.asp
    "min_res": "1040x331",                          # and http://store.steampowered.com/hwsurvey?platform=combined
    "800x600": "800x600",                           # storen in this dictionary for lookup of important resolutions
    "1280x720": "1280x720",                         # and for easy access with autocompletion
    "1024x768": "1024x768",
    "1360x768": "1360x768",
    "1366x768": "1366x768",
    "1280x800": "1280x800",
    "1500x800": "1500x800",
    "1536x864": "1536x864",
    "1440x900": "1440x900",
    "1600x900": "1600x900",
    "1280x1024": "1280x1024",
    "1680x1050": "1680x1050",
    "1920x1080": "1920x1080",
    "1920x1200": "1920x1200",
    "2560x1440": "2560x1440"
}
