# -*- coding: utf-8 -*-

import libavg
from libavg import widget, avg
import global_values
import pat_model
import util

COLOR_SCHEME = 0            # user color scheme (see global_values.py for color schemes)


class OptionsPanel(libavg.DivNode):
    def __init__(self, users, vis_params, parent, **kwargs):
        super(OptionsPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.__vis_params = vis_params
        self.parent_div = parent        # parent node

        # rect for coloured border and background
        self.background_rect = libavg.RectNode(pos=(0, 0), size=self.size, parent=self, strokewidth=1, fillopacity=1,
                                               color=global_values.COLOR_BACKGROUND,
                                               fillcolor=global_values.COLOR_BACKGROUND)

        """play/pause button"""
        icon_size = (15, 15)
        button_size = (30, 30)
        # rect for play button border
        self.play_rect = libavg.RectNode(pos=(0, 0), size=button_size, parent=self,
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
                                               pos=(0, self.play_rect.pos[1]), size=button_size, parent=self)
        self.play_button.subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__play_pause(checked))

        """user toggle buttons"""
        # user buttons
        self.user_buttons = []
        self.user_texts = []
        for i in range(len(users)):
            user_color = util.get_user_color_as_hex(i, 1)
            size = (70, 30)
            self.user_buttons.append(
                widget.ToggleButton(uncheckedUpNode=
                                    avg.RectNode(size=size, fillopacity=0, strokewidth=1, color=user_color),
                                    uncheckedDownNode=
                                    avg.RectNode(size=size, fillopacity=0, strokewidth=1, color=user_color),
                                    checkedUpNode=
                                    avg.RectNode(size=size, fillopacity=1, strokewidth=1, color=user_color, fillcolor=user_color),
                                    checkedDownNode=
                                    avg.RectNode(size=size, fillopacity=1, strokewidth=1, color=user_color, fillcolor=user_color),
                                    pos=(i * 80 + 50, 0), size=size, parent=self))
            self.user_buttons[i].checked = True
            self.user_texts.append(avg.WordsNode(color=global_values.COLOR_BACKGROUND,
                                                 parent=self, sensitive=False, text="User {}".format(i + 1),
                                                 alignment="center"))
            self.user_texts[i].pos = (self.user_buttons[i].pos[0] + self.user_buttons[i].width/2,
                                      self.user_buttons[i].pos[1] + 6)
            self.user_buttons[i].subscribe(widget.CheckBox.TOGGLED,
                    lambda checked, user_id=i: self.__toggle_user(checked, user_id=user_id))

        """smoothness slider"""
        # smoothness text
        self.smoothness_text = avg.WordsNode(pos=(500, 0), color=global_values.COLOR_FOREGROUND,
                                             parent=self)
        self.__update_smoothness_text()

        # smoothness slider
        smoothness_range = vis_params.MIN_SMOOTHNESS_FACTOR, vis_params.MAX_SMOOTHNESS_FACTOR
        self.smoothness_slider = widget.Slider(pos=(495, 20), width=180, range=smoothness_range, parent=self)
        self.smoothness_slider.thumbPos = self.__vis_params.get_smoothness_factor()
        # subscription to change curve smoothness
        self.smoothness_slider.subscribe(widget.Slider.THUMB_POS_CHANGED, self.__on_smoothness_change)

        # legend
        self.legend = Legend(parent=self, min_value=0, max_value=1, unit="m", size=(210, 200))
        self.legend.pos = (self.width - self.legend.width, self.height - self.legend.height)

        self.__vis_params.subscribe(self.__vis_params.CHANGED, self.update_time)

    def __on_smoothness_change(self, pos):
        self.__vis_params.set_smoothness_factor(pos)
        self.__vis_params.notify()

    def __toggle_user(self, checked, user_id):
        self.__vis_params.set_user_visible(user_id, checked)

    def __play_pause(self, checked):
        self.parent_div.play_pause()

    def update_time(self, vis_params):
        if self.play_button.checked is not vis_params.is_playing:
            self.play_button.checked = vis_params.is_playing
        self.__update_smoothness_text()

    def __update_smoothness_text(self):
        self.smoothness_text.text = "Smoothness: {:1.2f}".format(
                self.__vis_params.get_smoothness_factor())


class Legend(libavg.DivNode):
    def __init__(self, parent, min_value, max_value, unit, **kwargs):
        super(Legend, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.sensitive = False

        points = []
        dists = []

        for i in range(0, 101):
            value = i / 100.0
            points.append(libavg.Point2D(self.width * value, self.height))
            dists.append(value)

        data_div = parent.getParent().main_visualization.data_div
        var_line_div = libavg.DivNode(pos=(0, 0), size=(self.width, self.height), crop=True, parent=self)
        max_width = (min(data_div.width, data_div.height) / 12)
        line = vwline.VWLineNode(color=util.get_user_color_as_hex(-1, 1), maxwidth=max_width, parent=var_line_div)
        line.setValues(points, dists)

        # texts
        libavg.WordsNode(pos=(0, self.height - 35), text="Distance from wall", parent=self,
                         color=global_values.COLOR_FOREGROUND)
        pos_range = pat_model.pos_range
        libavg.WordsNode(pos=(0, self.height - 20), text="{} {}".format(str(int(pos_range[0][2])), unit),
                         parent=self, color=global_values.COLOR_FOREGROUND, alignment="right")
        libavg.WordsNode(pos=(self.width + 2, self.height - 20), parent=self, alignment="left",
                         text="{} {}".format(str(int(pos_range[1][2])), unit),
                         color=global_values.COLOR_FOREGROUND, )
