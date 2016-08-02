# -*- coding: utf-8 -*-

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
