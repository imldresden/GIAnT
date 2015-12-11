from libavg import app
import libavg
import User
import Visualization
import time
import colorsys


class main_drawer(app.MainDiv):
    user_colors = []

    def init_colors(self):
        self.user_colors.append(colorsys.hsv_to_rgb(1 / float(4), 1, 1))
        self.user_colors.append(colorsys.hsv_to_rgb(2 / float(4), 1, 1))
        self.user_colors.append(colorsys.hsv_to_rgb(3 / float(4), 1, 1))
        self.user_colors.append(colorsys.hsv_to_rgb(4 / float(4), 1, 1))
        for color_index in range(len(self.user_colors)):
            color = list(self.user_colors[color_index])
            color = (color[0] * 255, color[1] * 255, color[2] * 255)
            color = '%02x%02x%02x' % color
            self.user_colors[color_index] = color

    last_time = 0
    visualizations = []
    resolution = (1920, 1000)

    viewport_change_duration = 1

    zoom_target = 1
    zoom_current = 1
    zoom_last = 1
    zoom_amount = 0.1
    zoom_change_progress = 0
    zoom_change_starttime = 0

    shift_target = 0.5
    shift_current = 0.5
    shift_last = 0.5
    shift_change_progress = 0
    shift_change_starttime = 0

    def onInit(self):
        self.init_colors()
        self.resolution = libavg.app.instance._windowSize
        libavg.RectNode(pos=(0, 0), size=self.resolution, fillopacity=1, fillcolor='ffffff', parent=self)
        for userid in range(1, 5):
            user = User.User(userid, self.user_colors[userid - 1])
        self.visualizations.append(Visualization.Visualization(self, (1920, 1000), (100, 100)))
        app.keyboardmanager.bindKeyDown(text='+', handler=self.zoomIn)
        app.keyboardmanager.bindKeyDown(text='-', handler=self.zoomOut)
        app.keyboardmanager.bindKeyDown(text='2', handler=self.shift_forward)
        app.keyboardmanager.bindKeyDown(text='8', handler=self.shift_back)

    def onFrame(self):
        # print 1 / (time.time() - self.last_time) # FPS
        self.last_time = time.time()
        if self.zoom_change_starttime != 0 or self.shift_change_starttime != 0:
            if self.zoom_change_starttime != 0:
                if self.zoom_change_progress == 1:
                    self.zoom_last = self.zoom_target
                    self.zoom_change_starttime = 0
                    return

                self.zoom_change_progress = (time.time() - self.zoom_change_starttime) / self.viewport_change_duration
                self.zoom_change_progress = min(1, self.zoom_change_progress)

                self.zoom_current = self.zoom_last * (
                    1 - self.zoom_change_progress) + self.zoom_target * self.zoom_change_progress

            if self.shift_change_starttime != 0:
                if self.shift_change_progress == 1:
                    self.shift_last = self.shift_target
                    self.shift_change_starttime = 0
                    return

                self.shift_change_progress = (time.time() - self.shift_change_starttime) / self.viewport_change_duration
                self.shift_change_progress = min(1, self.shift_change_progress)

                self.shift_current = self.shift_last * (
                    1 - self.shift_change_progress) + self.shift_target * self.shift_change_progress
            for visualization in self.visualizations:
                visualization.start = (self.zoom_current - 1) * self.shift_current
                visualization.end = 1 - (self.zoom_current - 1) * (1 - self.shift_current)
                visualization.createLine()
                
    def drawLine(self, p1, p2, color, thickness, opacity):
        return libavg.LineNode(pos1=p1, pos2=p2, color=color, strokewidth=thickness, parent=self,
                               opacity=opacity)

    def shift_back(self):
        try:
            self.shift_last = self.shift_current
            self.shift_target = min(1, max(0, self.shift_target - 0.01 / (self.zoom_target - 1)))
            print str(self.shift_target)
            self.shift_change_starttime = time.time()
            self.shift_change_progress = 0
        except:
            None

    def shift_forward(self):
        try:
            self.shift_last = self.shift_current
            self.shift_target = min(1, max(0, self.shift_target + 0.01 / (self.zoom_target - 1)))
            self.shift_change_starttime = time.time()
            self.shift_change_progress = 0
        except:
            None

    def zoomIn(self):
        self.zoom_last = self.zoom_current
        # self.zoom_target += (1.5 - self.zoom_target) * self.zoom_amount
        self.zoom_target += (2 - self.zoom_target) / float(5)
        self.zoom_change_starttime = time.time()
        self.zoom_change_progress = 0

    def zoomOut(self):
        self.zoom_last = self.zoom_current
        strength = (1.5 - self.zoom_target) * self.zoom_amount
        # self.zoom_target -= self.zoom_target / ((1 / strength) + 1)
        self.zoom_target -= (2 - self.zoom_target) / float(4)
        self.zoom_target = max(1, self.zoom_target)
        self.zoom_change_starttime = time.time()
        self.zoom_change_progress = 0
