#!/usr/bin/env python
# -*- coding: utf-8 -*-

from global_values import resolution

import time
from libavg import app, avg
import libavg
import vis_params
import movement_panel
import axis
import OptionsPanel
import global_values
import Legend
import video


class MainDiv(app.MainDiv):
    last_time = 0
    viewport_change_duration = 0.3

    def onInit(self):
        # main_drawer Div has margin to all sides of application window
        margin = global_values.APP_MARGIN
        # and padding inbetween elements of visualization
        padding = global_values.APP_PADDING

        # position and scale main div
        self.pos = (margin, margin)
        res_x = libavg.app.instance._resolution[0] - 2 * margin
        res_y = libavg.app.instance._resolution[1] - 2 * margin

        # set aspect ratio for main visualization and elements on the right side
        main_vis_width = 2.0 / 3.0 * res_x
        menu_height = 50
        side_vis_height = 1.0 / 3.0 * res_y
        self.__vis_params = vis_params.VisParams()

        # rectangle to color background
        libavg.RectNode(parent=self, pos=(-1000, -1000), size=(10000, 10000),
                        strokewidth=0, fillcolor=global_values.COLOR_BACKGROUND, fillopacity=1)

        # cosmetics (abstract wall image on left side of main visualization and wall front visualization)
        self.__cosmetics_wall = libavg.PolygonNode(parent=self, opacity=0, fillopacity=1,
                                                   fillcolor=global_values.COLOR_DARK_GREY)
        self.__cosmetics_main = libavg.PolygonNode(parent=self, opacity=0, fillopacity=1,
                                                   fillcolor=global_values.COLOR_DARK_GREY)
        self.__cosmetics_main_screen = libavg.PolygonNode(parent=self, opacity=0, fillopacity=1,
                                                          fillcolor=global_values.COLOR_BLACK)

        # main visualization
        self.main_visualization = movement_panel.MovementPanel(
                parent=self, vis_params=self.__vis_params, pos=(0, 0), size=(main_vis_width, res_y - menu_height))

        # video
        self.video = video.Video(pos=(main_vis_width + padding + axis.THICKNESS,
                                      2 * side_vis_height - 1.5 * axis.THICKNESS + padding),
                                 size=(res_x - main_vis_width - padding - axis.THICKNESS,
                                       side_vis_height + 1.5 * axis.THICKNESS - padding),
                                 vis_params=self.__vis_params, parent=self)

        # nodes needed in self.menu
        nodes = [self.main_visualization]

        # menu
        self.options = OptionsPanel.OptionsPanel(nodes=nodes, vis_params=self.__vis_params, parent=self,
                                                 pos=(0, self.main_visualization.height),
                                                 size=(self.main_visualization.width, menu_height))

        # legend
        self.legend = Legend.Legend(parent=self.options, min_value=0, max_value=1, unit="cm", size=(210, 200))
        self.legend.pos = (self.options.width - self.legend.width, menu_height - self.legend.height)

        self.draw_cosmetics()

        self.main_visualization.subscribe(avg.Node.MOUSE_WHEEL, self.onMouseWheel)
        app.keyboardmanager.bindKeyDown(keyname='Right', handler=self.shift_forward)
        app.keyboardmanager.bindKeyDown(keyname='Left', handler=self.shift_back)
        app.keyboardmanager.bindKeyDown(keyname='Up', handler=self.zoom_in)
        app.keyboardmanager.bindKeyDown(keyname='Down', handler=self.zoom_out)
        app.keyboardmanager.bindKeyDown(keyname='Space', handler=self.play_pause)

    def onFrame(self):
        if self.__vis_params.play:
            current_time = time.time()
            self.__vis_params.shift_time(True, (current_time - self.__vis_params.last_frame_time) * 1000)
            self.__vis_params.last_frame_time = current_time

    def draw_line(self, p1, p2, color, thickness, last_thickness, opacity):
        return libavg.LineNode(pos1=p1, pos2=p2, color=color, strokewidth=thickness, parent=self)

    def draw_line_variable_thickness(self, color, opacity, p1, p2, p3, p4, thickness1, thickness2, thickness3,
                                     thickness4, newNode=True):
        start_points = calculate_line_intersection(p1, p2, p3, thickness1, thickness2, thickness3)
        end_points = calculate_line_intersection(p2, p3, p4, thickness2, thickness3, thickness4)
        if newNode:
            return libavg.PolygonNode(pos=[start_points[0], end_points[0], end_points[1], start_points[1]],
                                      opacity=opacity, color=color, parent=self)
        return [start_points[0], end_points[0], end_points[1], start_points[1]]

    def zoom_in(self):
        self.__vis_params.zoom_in_at(0.5)

    def zoom_out(self):
        self.__vis_params.zoom_out_at(0.5)

    def shift_back(self):
        self.__vis_params.shift_time(False)

    def shift_forward(self):
        self.__vis_params.shift_time(True)

    def onMouseWheel(self, event):
        if event.motion.y > 0:
            self.__vis_params.zoom_in_at((event.pos[0] - axis.THICKNESS) / (self.main_visualization.width - axis.THICKNESS))
        else:
            self.__vis_params.zoom_out_at((event.pos[0] - axis.THICKNESS) / (self.main_visualization.width - axis.THICKNESS))

    def play_pause(self):
        self.__vis_params.play_animation()
        self.video.play_pause(self.__vis_params.play)

    def draw_cosmetics(self):
        """
        Position cosmetic wall image left of the main visualization and wall image behind wall visualization.
        """
        # set position of cosmetic wall image left of the main visualization
        main_pos = (self.main_visualization.pos[0] + axis.THICKNESS, self.main_visualization.pos[1])
        main_size = (self.main_visualization.width - axis.THICKNESS, self.main_visualization.size[1] - axis.THICKNESS)
        cos_offset = 9
        cos_vis_offset = 4
        cos_screen_offset = 2
        cos_wall_width = 16
        # space from bottom of y-axis to left side of display-wall
        cos_wall_start = value_to_pixel(global_values.x_wall_range[0], main_size[1], global_values.x_range)
        # space from top of y-axis to right side of display-wall
        cos_wall_end = value_to_pixel(global_values.wall_width, main_size[1], global_values.x_range)

        self.__cosmetics_main.pos = (
            (main_pos[0] - cos_vis_offset, main_size[1] - cos_wall_end),  # top right
            (main_pos[0] - cos_vis_offset, main_size[1] - cos_wall_start),  # bottom right
            (main_pos[0] - cos_vis_offset - cos_wall_width, main_size[1] - cos_wall_start),  # bottom mid
            (main_pos[0] - cos_vis_offset - cos_wall_width - cos_offset, main_size[1] - cos_offset - cos_wall_start),  # bottom left
            (main_pos[0] - cos_vis_offset - cos_wall_width - cos_offset, main_size[1] - cos_wall_end - cos_offset),  # top left
            (main_pos[0] - cos_vis_offset - cos_offset, main_size[1] - cos_wall_end - cos_offset))  # top mid
        self.__cosmetics_main_screen.pos = (
            (main_pos[0] - cos_vis_offset - cos_screen_offset, main_size[1] - cos_wall_end + cos_screen_offset),
            (main_pos[0] - cos_vis_offset - cos_screen_offset, main_size[1] - cos_wall_start - cos_screen_offset),
            (main_pos[0] - cos_vis_offset - cos_offset, main_size[1] - cos_wall_start - cos_offset - cos_screen_offset),
            (main_pos[0] - cos_vis_offset - cos_offset, main_size[1] - cos_wall_end - cos_offset + cos_screen_offset))


def value_to_pixel(value, max_px, interval):
    """
    Calculate pixel position.
    :param value: Value to be converted into pixel position
    :param max_px: Maximum possible value
    :param interval: Current interval
    :return: pixel position
    """
    a = (interval[1] - interval[0]) / max_px
    return value / a - interval[0] / a


"""start parameter"""
OptionsPanel.SHOW_F_FORMATIONS = True
OptionsPanel.LOAD_F_FORMATIONS = True
OptionsPanel.COLOR_SCHEME = 0

# minimum recommended resolution: 1040x331 px!
app.App().run(MainDiv(), app_resolution=resolution["1500x800"])
