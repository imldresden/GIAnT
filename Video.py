# -*- coding: utf-8 -*-

import libavg
from libavg import avg
from database import load_file
from time_interval import main_time_frame
import global_values
import util


class Video:
    offset = (60 * 6 + 8.8) * 1000  # video is offset from data by this amount (ms)

    def __init__(self, pos, size, parent):
        self.path = ""
        file_paths = load_file('csv/filelist.txt')
        video_extensions = ["mpg", "mpeg", "mpeg2", "mpeg4",  "xvid", "mjpeg", "vp6", "h264"]
        for file_path in file_paths:
            path = file_path[0].lower()
            if path.endswith(".csv"):
                continue

            if path.endswith(tuple(video_extensions)):
                self.path = "csv/"+file_path[0]
                break
        self.frames = 0
        vid_size = (size[0], size[0] * 9.0 / 16.0)
        if size[0] / size[1] > 16.0 / 9.0:
            vid_size = (size[1] * 16.0 / 9.0, size[1])

        pos = (pos[0] + (size[0] - vid_size[0]) / 2, pos[1] + (size[1] - vid_size[1]) / 2)

        self.is_playing = False
        self.videoNode = avg.VideoNode(href=self.path, pos=pos,
                                       parent=parent, size=vid_size, loop=True,
                                       mipmap=True,
                                       enablesound=False)

        # rectangle for border
        libavg.RectNode(parent=parent, pos=pos, size=vid_size, strokewidth=1, color=global_values.COLOR_FOREGROUND)
        self.__cur_time_text = libavg.WordsNode(color=global_values.COLOR_FOREGROUND, parent=parent,
                                                pos=(pos[0], pos[1] + vid_size[1]), text="")

        self.videoNode.volume = 0
        try:
            self.videoNode.play()
            self.videoNode.pause()

            main_time_frame.subscribe(self)
        except:
            print "No video found"

    def update_time_frame(self, time_frame, draw_lines):
        if not self.is_playing:
            if self.frames % 3 == 0:
                self.videoNode.seekToTime(int(main_time_frame.highlight_time + self.offset))
            self.frames += 1
        self.__cur_time_text.text = "Current time: {}".format(
            util.format_label_value(unit="ms", value=self.videoNode.getCurTime() - self.offset, short=True))

    def play_pause(self, play=True):
        start_time = main_time_frame.get_interval_range()[0]
        self.is_playing = play
        time = int(start_time + self.offset)
        self.videoNode.seekToTime(time)
        if play:
            self.videoNode.play()
        else:
            self.videoNode.pause()
