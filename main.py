#!/usr/bin/env python
# -*- coding: utf-8 -*-

from global_values import resolution

from libavg import app, avg
import libavg
import vis_params
import movement_panel
import axis
import options_panel
import global_values
import video_panel
import pat_model
import custom_slider


class MainDiv(app.MainDiv):
    last_time = 0
    viewport_change_duration = 0.3

    def onInit(self):
        # main_drawer Div has margin to all sides of application window
        margin = global_values.APP_MARGIN
        # and padding inbetween elements of visualization
        padding = global_values.APP_PADDING

        self.session = pat_model.create_session()

        # position and scale main div
        self.pos = (margin, margin)
        res_x = self.size[0] - 2 * margin
        res_y = self.size[1] - 2 * margin

        # set aspect ratio for main visualization and elements on the right side
        main_vis_width = 2.0 / 3.0 * res_x
        menu_height = 50
        side_vis_height = 1.0 / 3.0 * res_y
        self.__vis_params = vis_params.VisParams(self.session)

        # rectangle to color background
        libavg.RectNode(parent=self, pos=(-1000, -1000), size=(10000, 10000),
                        strokewidth=0, fillcolor=global_values.COLOR_BACKGROUND, fillopacity=1)

        self.main_visualization = movement_panel.MovementPanel(
                parent=self, session=self.session, vis_params=self.__vis_params, pos=(0, 0),
                size=(main_vis_width, res_y - menu_height))

        self.video = video_panel.VideoPanel(
                filename=self.session.data_dir + "/" + self.session.video_filename,
                pos=(main_vis_width + padding + axis.THICKNESS, 2 * side_vis_height - 1.5 * axis.THICKNESS + padding),
                size=(res_x - main_vis_width - padding - axis.THICKNESS,
                        side_vis_height + 1.5 * axis.THICKNESS - padding),
                time_offset=self.session.get_video_time_offset(),
                vis_params=self.__vis_params,
                parent=self)

        self.options = options_panel.OptionsPanel(users=self.session.users, vis_params=self.__vis_params, parent=self,
                                                 pos=(0, self.main_visualization.height),
                                                 size=(self.main_visualization.width, menu_height))

        # interval scrollbar
        bar_pos = (48, self.main_visualization.size.y-25)
        bar_range = (0, self.session.duration)
        self.__time_bar = custom_slider.IntervalScrollBar(pos=bar_pos, width=self.main_visualization.size.x-48,
                range=bar_range, thumbExtent=bar_range[1], parent=self)
        self.__time_bar.subscribe(custom_slider.IntervalScrollBar.THUMB_POS_CHANGED, self.__on_scroll)

        self.__vis_params.subscribe(self.__vis_params.CHANGED, self.__on_update_time)
        self.__vis_params.subscribe(self.__vis_params.IS_PLAYING, self.__on_play_pause)

        app.keyboardmanager.bindKeyDown(keyname='Right', handler=self.shift_forward, help="Step forward")
        app.keyboardmanager.bindKeyDown(keyname='Left', handler=self.shift_back, help="Step back")
        app.keyboardmanager.bindKeyDown(keyname='Up', handler=self.zoom_in, help="Zoom in")
        app.keyboardmanager.bindKeyDown(keyname='Down', handler=self.zoom_out, help="Zoom out")
        app.keyboardmanager.bindKeyDown(keyname='Space', handler=self.play_pause, help="Play/pause")
        for i in range(0,4):
            app.keyboardmanager.bindKeyDown(keyname=str(i+1),
                    handler=lambda userid=i: self.toggle_user_visible(userid),
                    help = "Toggle user "+str(i+1))

    def zoom_in(self):
        self.__vis_params.zoom_in_at(0.5)

    def zoom_out(self):
        self.__vis_params.zoom_out_at(0.5)

    def shift_back(self):
        self.__vis_params.shift_time(False)

    def shift_forward(self):
        self.__vis_params.shift_time(True)

    def play_pause(self):
        self.__vis_params.is_playing = not self.__vis_params.is_playing

    def toggle_user_visible(self, userid):
        is_visible = self.__vis_params.get_user_visible(userid)
        self.__vis_params.set_user_visible(userid, not is_visible)

    def __on_scroll(self, pos):
        # update global time interval
        delta = pos - self.__vis_params.get_time_interval()[0]
        self.__vis_params.highlight_time += delta
        interval = pos, pos + self.__time_bar.thumbExtent
        self.__vis_params.set_time_interval(interval)

    def __on_play_pause(self, playing):
        self.__time_bar.sensitive = not playing

    def __on_update_time(self, vis_params):
        interval = vis_params.get_time_interval()
        self.__time_bar.setThumbPos(interval[0])
        self.__time_bar.setThumbExtent(interval[1] - interval[0])


def value_to_pixel(value, max_px, interval):
    a = (interval[1] - interval[0]) / max_px
    return (value - interval[0]) / a


# minimum recommended resolution: 1040x331 px!
app.App().run(MainDiv(), app_resolution=resolution["1500x800"])
