# -*- coding: utf-8 -*-

import libavg
from libavg import widget, avg
import custom_slider
import helper
import global_values


class OptionsPanel(libavg.DivNode):
    def __init__(self, vis_params, duration, parent, **kwargs):
        super(OptionsPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.__vis_params = vis_params
        self.parent_div = parent        # parent node
        self.__duration = duration

        # rect for coloured border and background
        self.background_rect = libavg.RectNode(pos=(0, 0), size=self.size, parent=self, strokewidth=1, fillopacity=1,
                                               color=global_values.COLOR_BACKGROUND,
                                               fillcolor=global_values.COLOR_BACKGROUND)

        """play/pause button"""
        icon_size = (15, 15)
        button_size = (30, 30)
        # rect for play button border
        self.play_rect = libavg.RectNode(pos=(6, 22), size=button_size, parent=self,
                                         strokewidth=1, fillopacity=0, color=global_values.COLOR_FOREGROUND,
                                         sensitive=False)
        # play button
        icon_h_size = (icon_size[0]/2, icon_size[1]/2)
        self.play_button = widget.ToggleButton(uncheckedUpNode=
                                               avg.ImageNode(href="images/play.png", pos=icon_h_size, size=icon_size),
                                               uncheckedDownNode=
                                               avg.ImageNode(href="images/play.png", pos=icon_h_size, size=icon_size),
                                               checkedUpNode=
                                               avg.ImageNode(href="images/pause.png", pos=icon_h_size, size=icon_size),
                                               checkedDownNode=
                                               avg.ImageNode(href="images/pause.png", pos=icon_h_size, size=icon_size),
                                               pos=self.play_rect.pos, size=button_size, parent=self)
        self.play_button.subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__play_pause(checked))

        self.__init_time_bar(duration)
#        self.__init_smoothness_slider()

        self.__vis_params.subscribe(self.__vis_params.CHANGED, self.__update_time)
        self.__vis_params.subscribe(self.__vis_params.IS_PLAYING, self.__on_play_pause)

    def __init_time_bar(self, duration):
        pos = avg.Point2D(58, 0)
        size = avg.Point2D(self.width - pos.x - 10, 60)
        self.__time_bar = avg.DivNode(pos=pos, size=size,  parent=self)

        avg.WordsNode(pos=(0,0), color=global_values.COLOR_FOREGROUND, fontsize=global_values.FONT_SIZE,
                text="Time range", parent=self.__time_bar)

        self.__time_slider = custom_slider.IntervalScrollBar(pos=(0,27), width=size.x,
                range=(0, duration), thumbExtent=duration, parent=self.__time_bar)
        self.__time_slider.subscribe(custom_slider.IntervalScrollBar.THUMB_POS_CHANGED, self.__on_scroll)

        self.__start_label = avg.WordsNode(pos=(0,48), color=global_values.COLOR_FOREGROUND,
                text="0:00", fontsize=global_values.FONT_SIZE, parent=self.__time_bar)
        self.__end_label = avg.WordsNode(pos=(size.x,48), color=global_values.COLOR_FOREGROUND,
                text=helper.format_time(duration, False), alignment="right", fontsize=global_values.FONT_SIZE,
                parent=self.__time_bar)
        self.__cur_time_line = avg.LineNode(color=global_values.COLOR_WHITE,
                sensitive=False, parent=self.__time_bar)
        self.__cur_time_label = avg.WordsNode(pos=(size.x,0), color=global_values.COLOR_FOREGROUND, alignment="right",
                fontsize = global_values.FONT_SIZE, parent=self.__time_bar)

    def __init_smoothness_slider(self):
        pos = avg.Point2D(self.width - 180, 0)

        avg.WordsNode(pos=pos+(4,0), color=global_values.COLOR_FOREGROUND, fontsize=global_values.FONT_SIZE,
                text="Smoothness", parent=self)

        smoothness_range = self.__vis_params.MIN_SMOOTHNESS_FACTOR, self.__vis_params.MAX_SMOOTHNESS_FACTOR
        self.smoothness_slider = widget.Slider(pos=pos+(0,33), width=180, range=smoothness_range, parent=self)
        self.smoothness_slider.thumbPos = self.__vis_params.get_smoothness_factor()
        self.smoothness_slider.subscribe(widget.Slider.THUMB_POS_CHANGED, self.__on_smoothness_change)

    def __on_smoothness_change(self, pos):
        self.__vis_params.set_smoothness_factor(pos)
        self.__vis_params.notify()

    def __on_scroll(self, pos):
        # update global time interval
        delta = pos - self.__vis_params.get_time_interval()[0]
        self.__vis_params.highlight_time += delta
        interval = pos, pos + self.__time_slider.thumbExtent
        self.__vis_params.set_time_interval(interval)

    def __play_pause(self, checked):
        self.__vis_params.is_playing = not self.__vis_params.is_playing

    def __update_time(self, vis_params):
        interval = vis_params.get_time_interval()
        self.__time_slider.setThumbPos(interval[0])
        self.__time_slider.setThumbExtent(interval[1] - interval[0])
        cur_time = vis_params.highlight_time
        line_x = (cur_time/self.__duration)*self.__time_slider.width
        self.__cur_time_line.pos1 = (line_x, 23)
        self.__cur_time_line.pos2 = (line_x, 50)
        self.__cur_time_label.text = "Current time: " + helper.format_time(cur_time, False)

    def __on_play_pause(self, playing):
        self.__time_slider.sensitive = not playing
        self.play_button.checked = self.__vis_params.is_playing

