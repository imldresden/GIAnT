#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libavg import app, avg
import libavg
import vis_params
import movement_panel
import wall_panel
import floor_panel
import video_panel
import options_panel
import global_values
import pat_model


class MainDiv(app.MainDiv):
    last_time = 0
    viewport_change_duration = 0.3

    def onInit(self):
        self.session = pat_model.create_session()
        self.session.load_from_db()
        self.__vis_params = vis_params.VisParams(self.session)
#        self.elementoutlinecolor="FF0000"

        padding = global_values.APP_PADDING  # and padding inbetween elements of visualization
        menu_height = 50

        margin = global_values.APP_MARGIN    # distance to all sides of application window
        self.pos = (margin, margin)
        self.size -= 2*avg.Point2D(margin, margin)

        # rectangle to color background
        libavg.RectNode(parent=self, pos=(-1000, -1000), size=(10000, 10000),
                        strokewidth=0, fillcolor=global_values.COLOR_BACKGROUND, fillopacity=1)

        # Visualization panels
        vis_area_size = avg.Point2D(self.width, self.height - menu_height - padding)
        panel_size = avg.Point2D(vis_area_size - (padding, padding)) / 2
        panel00_pos = (0,0)
        panel01_pos = (0, panel_size.y + padding)
        panel10_pos = (panel_size.x + padding, 0)

        self.timeline_panel = movement_panel.MovementPanel(pos=panel00_pos, size=panel_size,
                session=self.session, vis_params=self.__vis_params, parent=self)
        self.wall_panel = wall_panel.WallPanel(pos=panel10_pos, size=panel_size,
                session=self.session, vis_params=self.__vis_params, parent=self)
        panel11_pos = (panel_size.x + padding, self.wall_panel.height + 5)
        self.floor_panel = floor_panel.FloorPanel(pos=panel11_pos, size=panel_size,
                session=self.session, vis_params=self.__vis_params, parent=self)

        self.video = video_panel.VideoPanel(pos=panel01_pos, size=panel_size,
                filename=self.session.data_dir + "/" + self.session.video_filename,
                time_offset=self.session.get_video_time_offset(),
                vis_params=self.__vis_params, parent=self)

        options_pos = (0, self.height-menu_height)
        options_size = (self.width, menu_height)
        self.options = options_panel.OptionsPanel(pos=options_pos, size=options_size,
            vis_params=self.__vis_params, duration=self.session.duration, parent=self)

        app.keyboardmanager.bindKeyDown(keyname='Right', handler=self.shift_forward, help="Step forward")
        app.keyboardmanager.bindKeyDown(keyname='Left', handler=self.shift_back, help="Step back")
        app.keyboardmanager.bindKeyDown(keyname='Up', handler=self.zoom_in, help="Zoom in")
        app.keyboardmanager.bindKeyDown(keyname='Down', handler=self.zoom_out, help="Zoom out")
        app.keyboardmanager.bindKeyDown(keyname='Space', handler=self.play_pause, help="Play/pause")
        for i in range(0,4):
            app.keyboardmanager.bindKeyDown(keyname=str(i+1),
                    handler=lambda userid=i: self.toggle_user_visible(userid),
                    help = "Toggle user "+str(i+1))

        self.__vis_params.set_time_interval((0, self.session.duration))

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


def value_to_pixel(value, max_px, interval):
    a = (interval[1] - interval[0]) / max_px
    return (value - interval[0]) / a


app.App().run(MainDiv(), app_resolution="1500x1000")
