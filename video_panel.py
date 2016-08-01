# -*- coding: utf-8 -*-

import libavg
from libavg import avg, player
import global_values
import util


class VideoPanel(avg.DivNode):
    offset = 0.0  # video is offset from data by this amount (secs)

    def __init__(self, filename, vis_params, parent=None, **kwargs):
        super(VideoPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.path = filename
        size = self.size
        if size[0] / size[1] > 16.0 / 9.0:
            vid_size = (size[1] * 16.0 / 9.0, size[1])
        else:
            vid_size = (size[0], size[0] * 9.0 / 16.0)
        vid_pos = (size - vid_size)/2

        self.__vis_params = vis_params
        self.is_playing = False
        self.videoNode = avg.VideoNode(href=self.path, pos=vid_pos,
                                       parent=self, size=vid_size, loop=True,
                                       mipmap=True,
                                       threaded=False,
                                       enablesound=False)

        # rectangle for border
        libavg.RectNode(parent=self, pos=vid_pos, size=vid_size, strokewidth=1, color=global_values.COLOR_FOREGROUND)
        self.__cur_time_text = libavg.WordsNode(color=global_values.COLOR_FOREGROUND, parent=self,
                                                pos=(vid_pos + (0, vid_size[1])))

        self.videoNode.volume = 0

        self.videoNode.play()
        self.videoNode.pause()

        vis_params.subscribe(vis_params.CHANGED, self.update_time)
        player.subscribe(player.ON_FRAME, self.__time_changed)

    def update_time(self, vis_params):
        if not self.is_playing:
            self.videoNode.seekToTime(int((vis_params.highlight_time + self.offset)*1000))
            self.__update_time_label()

    def play_pause(self, play=True):
        self.is_playing = play
        if play:
            self.videoNode.play()
            self.__last_frame_time = self.videoNode.getCurTime()/1000.
        else:
            self.videoNode.pause()

    def __time_changed(self):
        if self.is_playing:
            cur_time = self.videoNode.getCurTime()/1000.
            time_change = cur_time - self.__last_frame_time
            self.__vis_params.shift_time(True, time_change)
            self.__last_frame_time = cur_time
            self.__update_time_label()

    def __update_time_label(self):
        self.__cur_time_text.text = "Current time: {}".format(
            util.format_label_value(unit="s", value=self.__vis_params.highlight_time))
