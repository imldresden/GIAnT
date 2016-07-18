# -*- coding: utf-8 -*-

import libavg
from libavg import widget, avg
from time_interval import main_time_frame
import global_values
import user
import util
import movement_panel
import time_interval

SHOW_F_FORMATIONS = True    # if f-formations are visible when app is launched
LOAD_F_FORMATIONS = True    # if f-formations are being loaded on startup (app needs to be restarted to load them)
COLOR_SCHEME = 1            # user color scheme (see global_values.py for color schemes)


class OptionsPanel(libavg.DivNode):
    def __init__(self, nodes, parent, **kwargs):
        """
        DivNode containing options.
        :param nodes: List with user-divs and f-formation-div. Needed to toggle visibility of these nodes
        :param parent: parent div node
        :param kwargs: passed through args for libavg.DivNode
        """
        super(OptionsPanel, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.nodes = nodes              # DivNodes containing user data
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
        for i in range(len(user.users)):
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
                                    pos=(i * 80 + 50, 0), size=size, parent=self, enabled=True))
            self.user_buttons[i].checked = True
            self.user_texts.append(avg.WordsNode(color=global_values.COLOR_BACKGROUND,
                                                 parent=self, sensitive=False, text="User {}".format(i + 1),
                                                 alignment="center"))
            self.user_texts[i].pos = (self.user_buttons[i].pos[0] + self.user_buttons[i].width/2,
                                      self.user_buttons[i].pos[1] + 6)

        # the lambda sets the user_id always as the largest i when put in above for loop
        self.user_buttons[0].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=0))
        self.user_buttons[1].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=1))
        self.user_buttons[2].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=2))
        self.user_buttons[3].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=3))

        """smoothness slider"""
        # smoothness text
        self.smoothness_text = avg.WordsNode(pos=(500, 0), color=global_values.COLOR_FOREGROUND,
                                             parent=self, text="Smoothness: {}s".format(
                                                 global_values.averaging_count * global_values.time_step_size / 1000))
        # smoothness slider
        self.smoothness_slider = widget.Slider(pos=(495, 20), width=180, parent=self, range=(2, 2000))
        self.smoothness_slider.thumbPos = global_values.averaging_count
        # subscription to change curve smoothness
        self.smoothness_slider.subscribe(widget.Slider.THUMB_POS_CHANGED, self.__on_smoothness_change)
        # smoothness default button
        icon_size = (12, 12)
        self.default_button = widget.ToggleButton(uncheckedUpNode=
                                                  avg.ImageNode(href="images/reload.png", pos=(0, 0), size=icon_size),
                                                  uncheckedDownNode=
                                                  avg.ImageNode(href="images/reload.png", pos=(0, 0), size=icon_size),
                                                  uncheckedDisabledNode=
                                                  avg.ImageNode(href="images/reload.png", pos=(0, 0), size=icon_size, opacity=0.25),
                                                  checkedUpNode=
                                                  avg.ImageNode(href="images/reload.png", pos=(0, 0), size=icon_size),
                                                  checkedDownNode=
                                                  avg.ImageNode(href="images/reload.png", pos=(0, 0), size=icon_size),
                                                  checkedDisabledNode=
                                                  avg.ImageNode(href="images/reload.png", pos=(0, 0), size=icon_size, opacity=0.25),
                                                  pos=(655, 3), size=icon_size, parent=self)
        # subscription to change smoothness to default on click
        self.default_button.subscribe(widget.CheckBox.TOGGLED,
                                      lambda pos: self.__default_smoothness(global_values.default_averaging_count))
        # link smoothness to zoom level button
        icon_size = (12, 12)
        button_size = (100, 12)
        self.link_s_button = widget.ToggleButton(uncheckedUpNode=
                                                 avg.RectNode(size=icon_size, fillopacity=0, strokewidth=1, color=global_values.COLOR_FOREGROUND),
                                                 uncheckedDownNode=
                                                 avg.RectNode(size=icon_size, fillopacity=0, strokewidth=1, color=global_values.COLOR_FOREGROUND),
                                                 uncheckedDisabledNode=
                                                 avg.RectNode(size=icon_size, fillopacity=0, strokewidth=1, color=global_values.COLOR_SECONDARY),
                                                 checkedUpNode=
                                                 avg.RectNode(size=icon_size, fillopacity=1, strokewidth=1, color=global_values.COLOR_FOREGROUND, fillcolor=global_values.COLOR_FOREGROUND),
                                                 checkedDownNode=
                                                 avg.RectNode(size=icon_size, fillopacity=1, strokewidth=1, color=global_values.COLOR_FOREGROUND, fillcolor=global_values.COLOR_FOREGROUND),
                                                 checkedDisabledNode=
                                                 avg.RectNode(size=icon_size, fillopacity=0, strokewidth=1, color=global_values.COLOR_SECONDARY),
                                                 pos=(500, 38), size=button_size, parent=self)
        self.__toggle_smoothness_link(global_values.link_smoothness)
        self.link_s_button.checked = global_values.link_smoothness
        self.link_s_text = avg.WordsNode(pos=(500 + button_size[1] + 5, 36), color=global_values.COLOR_FOREGROUND,
                                         parent=self, text="Link to Zoom", sensitive=False)
        # subscription to link smoothness to zoom level
        self.link_s_button.subscribe(widget.CheckBox.TOGGLED,
                                     lambda checked: self.__toggle_smoothness_link(checked))

        """subscribe to global time_frame"""
        main_time_frame.subscribe(main_time_frame.CHANGED, self.update_time)

    def __on_smoothness_change(self, pos):
        util.change_smoothness(pos)
        main_time_frame.notify()

    def __toggle_user(self, checked, user_id):
        """
        Toggles visibility of user with user_id. Checks self.nodes for Line_Visualization nodes and unlinks/appends
        user_divs within them.
        :param checked: bool, True when user is being toggled on
        :param user_id: user_id to toggle
        """
        if checked:
            user.users[user_id].selected = True
            for i, node in enumerate(self.nodes):
                if isinstance(node, movement_panel.MovementPanel):
                    node.data_div.appendChild(node.user_divs[user_id])
                    self.user_texts[user_id].color = global_values.COLOR_BACKGROUND
        else:
            user.users[user_id].selected = False
            for i, node in enumerate(self.nodes):
                if isinstance(node, movement_panel.MovementPanel):
                    node.user_divs[user_id].unlink()
                    self.user_texts[user_id].color = global_values.COLOR_FOREGROUND

        # publish changes
        main_time_frame.notify()

    def __default_smoothness(self, value):
        """
        Resets smoothness back to value.
        :param value: Smoothness value
        """
        util.change_smoothness(value)
        self.smoothness_slider.thumbPos = global_values.averaging_count

    def __toggle_smoothness_link(self, checked):
        """
        Links/Unlinks zooming and the curve smoothness. Disables smoothness slider and smoothness default button.
        :param checked: bool, True if link is active
        """
        global_values.link_smoothness = checked
        self.smoothness_slider.enabled = not checked
        self.default_button.enabled = not checked

        if checked:
            self.smoothness_slider.opacity = 0.2
            i_range = main_time_frame.get_interval_range()[1] - main_time_frame.get_interval_range()[0]
            s = i_range * (global_values.max_averaging_count - global_values.min_averaging_count) / time_interval.total_range_value
            util.change_smoothness(s)
        else:
            self.smoothness_slider.opacity = 1
            main_time_frame.notify()

    def __play_pause(self, checked):
        """
        Plays or pauses animation of visualizations and video playback.
        """
        self.parent_div.play_pause()

    def update_time(self, interval_obj, draw_lines):
        """
        Called by the publisher time_frame to update the visualization if changes are made.
        :param interval: (start, end): new interval start and end as list
        """
        if self.play_button.checked is not main_time_frame.play:
            self.play_button.checked = main_time_frame.play

        self.smoothness_text.text = "Smoothness: {}s".format(
            global_values.averaging_count * global_values.time_step_size / 1000.0)
        self.smoothness_slider.thumbPos = global_values.averaging_count
