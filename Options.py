import os
import libavg
from libavg import widget, avg
import global_values
import User
import Time_Frame
import Util


class Options(libavg.DivNode):

    def __init__(self, nodes, parent, **kwargs):
        super(Options, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.nodes = nodes  # DivNodes containing user data

        # rect for coloured border and background
        self.background_rect = libavg.RectNode(pos=(0, 0),
                                               size=self.size,
                                               parent=self, strokewidth=1, fillopacity=1,
                                               color=global_values.COLOR_BACKGROUND,
                                               fillcolor=global_values.COLOR_BACKGROUND)

        # customize checkbox skin
        curr_path = os.path.dirname(os.path.abspath(__file__))
        xml_file = "{}/skins/SimpleSkin.xml".format(curr_path)
        skin = libavg.widget.Skin(xml_file)

        self.user_buttons = []
        self.user_texts = []
        for i in range(len(User.users)):
            self.user_buttons.append(widget.CheckBox(pos=(20, (i + 1) * 20), size=(100, 100), parent=self, skinObj=skin))
            self.user_buttons[i].checked = True
            self.user_texts.append(avg.WordsNode(pos=(40, (i + 1) * 20), color=Util.get_user_color_as_hex(i, 1),
                                                 parent=self, text="User {}".format(i)))

        # TODO: the lambda has set the user_id always as the largest i (was always 3) when put in above for loop
        self.user_buttons[0].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=0))
        self.user_buttons[1].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=1))
        self.user_buttons[2].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=2))
        self.user_buttons[3].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=3))

        # smoothness slider
        self.smoothness_text = avg.WordsNode(pos=(20, 120), color=global_values.COLOR_FOREGROUND, parent=self,
                                             text="Smoothness: {}s".format(global_values.averaging_count*global_values.time_step_size/1000))
        self.smoothness_slider = widget.Slider(pos=(20, 150), width=self.width - 40, parent=self, range=(2, 2000))
        self.smoothness_slider.thumbPos = global_values.averaging_count
        self.smoothness_slider.subscribe(widget.Slider.THUMB_POS_CHANGED, lambda pos: self.__change_smoothness(pos))

        # subscribe to global time_frame
        Time_Frame.main_time_frame.subscribe(self)

    def __toggle_user(self, checked, user_id, event=None):
        if checked:
            User.users[user_id].selected = True
            for i, node in enumerate(self.nodes):
                node.data_div.appendChild(node.user_divs[user_id])
        else:
            User.users[user_id].selected = False
            for i, node in enumerate(self.nodes):
                node.user_divs[user_id].unlink()

        # publish changes
        Time_Frame.main_time_frame.publish()

    def __change_smoothness(self, value):
        global_values.averaging_count = int(value)
        self.smoothness_text.text = "Smoothness: {}s".format(global_values.averaging_count*global_values.time_step_size/1000.0)

        # publish changes
        Time_Frame.main_time_frame.publish()

    def update_time_frame(self, interval):
        """
        Called by the publisher time_frame to update the visualization to the new interval.
        :param interval: (start, end): new interval start and end as list
        """
        pass
