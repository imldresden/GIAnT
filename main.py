#!/usr/bin/env python
# -*- coding: utf-8 -*-
# GIAnT Group Interaction Analysis Toolkit
# Copyright (C) 2017 Interactive Media Lab Dresden
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from libavg import app, avg, player
import libavg
import vis_params
import movement_panel
import wall_panel
import floor_panel
import video_panel
import options_panel
import stats_panel
import global_values
import pat_model


class MainDiv(app.MainDiv):
    last_time = 0
    viewport_change_duration = 0.3

    def onInit(self):
        self.session = pat_model.create_session(3,1)
        self.session.load_from_db()
        self.__vis_params = vis_params.VisParams(self.session)
#        self.elementoutlinecolor="FF0000"

        padding = global_values.APP_PADDING  # and padding inbetween elements of visualization
        menu_height = 60

        margin = global_values.APP_MARGIN    # distance to all sides of application window
        self.pos = (margin, margin)
        self.size -= 2*avg.Point2D(margin, margin)

        # rectangle to color background
        libavg.RectNode(parent=self, pos=(-1000, -1000), size=(10000, 10000),
                        strokewidth=0, fillcolor=global_values.COLOR_BACKGROUND, fillopacity=1)

        # Visualization panels
        vis_area_size = avg.Point2D(self.width, self.height - menu_height - padding)
        panel_size = avg.Point2D(vis_area_size - (padding, padding)) / 2
        panel00_pos = avg.Point2D(0,0)
        panel01_pos = avg.Point2D(0, panel_size.y + padding)
        panel10_pos = avg.Point2D(panel_size.x + padding, 0)

        self.timeline_panel = movement_panel.MovementPanel(pos=panel00_pos, size=panel_size + (0,40),
                session=self.session, vis_params=self.__vis_params, is_dist_view=False, parent=self)
        self.__show_dist_view = False
        self.video = video_panel.VideoPanel(pos=panel01_pos+(0,40), size=panel_size - (0,40),
                filename=self.session.data_dir + "/" + self.session.video_filename,
                time_offset=self.session.get_video_time_offset(),
                vis_params=self.__vis_params, parent=self)

        self.wall_panel = wall_panel.WallPanel(pos=panel10_pos, size=panel_size,
                session=self.session, vis_params=self.__vis_params, parent=self)
        panel11_pos = avg.Point2D(panel_size.x + padding, self.wall_panel.height + 5)
        self.floor_panel = floor_panel.FloorPanel(pos=panel11_pos, size=panel_size,
                session=self.session, vis_params=self.__vis_params, parent=self)
        panel12_pos = panel11_pos + (0, self.floor_panel.height + 5)
        self.stats_panel = stats_panel.StatsPanel(pos=panel12_pos, size=(panel_size.x, vis_area_size.y - panel12_pos.y),
                session=self.session, vis_params=self.__vis_params, parent=self)

        options_pos = (0, self.height-menu_height)
        options_size = (self.width, menu_height)
        self.options = options_panel.OptionsPanel(pos=options_pos, size=options_size,
            vis_params=self.__vis_params, duration=self.session.duration, parent=self)

        app.keyboardmanager.bindKeyDown(keyname='Right', handler=self.shift_forward, help="Step forward")
        app.keyboardmanager.bindKeyDown(keyname='Left', handler=self.shift_back, help="Step back")
        app.keyboardmanager.bindKeyDown(keyname='Up', handler=self.zoom_in, help="Zoom in")
        app.keyboardmanager.bindKeyDown(keyname='Down', handler=self.zoom_out, help="Zoom out")
        app.keyboardmanager.bindKeyDown(keyname='Space', handler=self.play_pause, help="Play/pause")
        app.keyboardmanager.bindKeyDown(keyname='Q', handler=self.toggle_main_panel, help="Toggle timeline panel")
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

    def toggle_main_panel(self):
        self.__show_dist_view = not self.__show_dist_view
        pos = self.timeline_panel.pos
        size = self.timeline_panel.size
        self.timeline_panel.unlink()
        self.timeline_panel = movement_panel.MovementPanel(pos=pos, size=size,
                session=self.session, vis_params=self.__vis_params, is_dist_view=self.__show_dist_view, parent=self)
        self.__vis_params.notify()


    def toggle_user_visible(self, userid):
        is_visible = self.__vis_params.get_user_visible(userid)
        self.__vis_params.set_user_visible(userid, not is_visible)


def value_to_pixel(value, max_px, interval):
    a = (interval[1] - interval[0]) / max_px
    return (value - interval[0]) / a


player.setWindowTitle("GIAnT")
app.App().run(MainDiv(), app_resolution="1920x1200")
