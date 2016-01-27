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
            self.user_texts.append(avg.WordsNode(pos=(40, (i + 1) * 20), color=Util.get_user_color_as_hex(i, 1), parent=self,
                                                 text="User {}".format(i)))

        # TODO: the lambda has set the user_id always as the largest i (was always 3) when put in above for loop
        self.user_buttons[0].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=0))
        self.user_buttons[1].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=1))
        self.user_buttons[2].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=2))
        self.user_buttons[3].subscribe(widget.CheckBox.TOGGLED, lambda checked: self.__toggle_user(checked, user_id=3))

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
                # for child in range(node.user_divs[user_id].getNumChildren() - 1):
                #     print node.user_divs[user_id].unlink(child)
        Time_Frame.main_time_frame.publish()

    def update_time_frame(self, interval):
        """
        Called by the publisher time_frame to update the visualization to the new interval.
        :param interval: (start, end): new interval start and end as list
        """
        pass
