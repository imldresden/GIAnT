__author__ = 'KillytheBid'
from libavg import player, avg
import Time_Frame


class Video:
    offset = (60 * 6 + 8.8) * 1000
    path = ""
    def __init__(self, pos, size, parent):
        global path
        self.frames = 0
        vid_size = (size[0], size[0] * 9.0 / 16.0)
        if size[0] / size[1] > 16.0 / 9.0:
            vid_size = (size[1] * 16.0 / 9.0, size[1])

        pos = (pos[0] + (size[0] - vid_size[0]) / 2, pos[1] + (size[1] - vid_size[1]) / 2)

        self.is_playing = False
        self.videoNode = avg.VideoNode(href=path, pos=pos,
                                       parent=parent, size=vid_size, loop=True,
                                       mipmap=True,
                                       enablesound=False)
        self.videoNode.volume = 0
        self.videoNode.play()
        self.videoNode.pause()

        Time_Frame.main_time_frame.subscribe(self)

    def update_time_frame(self, time_frame, draw_lines):
        if not self.is_playing:
            if self.frames % 3 == 0:
                self.videoNode.seekToTime(int(Time_Frame.main_time_frame.highlight_time + self.offset))
            self.frames += 1

    def play_pause(self, play=True):
        self.is_playing = play
        time = int(Time_Frame.main_time_frame.get_interval_range()[1] + self.offset)
        self.videoNode.seekToTime(time)
        if play:
            self.videoNode.play()
        else:
            self.videoNode.pause()
