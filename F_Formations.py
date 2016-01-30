import Util
import math
import libavg
import User
import global_values
import Time_Frame
import time


class F_Formations(libavg.DivNode):

    def __init__(self, parent, **kwargs):
        super(F_Formations, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.f_duration = 100000          # duration of f-formation
        self.f_duration_px = self._value_to_pixel(self.f_duration, self.width, Time_Frame.total_range)
        self.f_formations = []          # contains all detected f_formation nodes
        self.f_formation_nodes = []

        # create tuple of users to check against existing f-formation
        user_list = []
        for i in range(len(User.users)):
            for j in range(len(User.users)):
                if j > i:
                    user_list.append((i, j))

        print "Searching for F-Formations..."
        start_time = time.time()

        # for each user-to-user connection
        for i, users in enumerate(user_list):
            t = Time_Frame.total_range[0]
            timer = 0
            self.flag = False
            # go through time by global_values.time_step_size steps
            while t < Time_Frame.total_range[1]:
                pos_values_1 = User.users[users[0]].get_head_position_averaged(int(t/global_values.time_step_size))
                pos_values_2 = User.users[users[1]].get_head_position_averaged(int(t/global_values.time_step_size))
                dir_values_1 = User.users[users[0]].get_view_point_averaged(int(t/global_values.time_step_size))
                dir_values_2 = User.users[users[1]].get_view_point_averaged(int(t/global_values.time_step_size))
                p1 = (pos_values_1[0], pos_values_1[1])
                p2 = (pos_values_2[0], pos_values_2[1])
                v1 = (dir_values_1[0], dir_values_1[1])
                v2 = (dir_values_2[0], dir_values_2[1])

                formation = self.check_for_f_formation(p1, p2, v1, v2)

                if formation >= 1:
                    if timer >= self.f_duration:
                        self.flag = True
                    timer += global_values.time_step_size
                else:
                    if self.flag:
                        # time, dur, user1, user2
                        self.f_formations.append([t, timer, users[0], users[1]])
                        self.flag = False
                    timer = 0

                t += global_values.time_step_size

        print "Searching for F-Formations done ({}s).".format(round((time.time() - start_time), 3))

        # initial update
        self.update_time_frame(Time_Frame.total_range)

    def check_for_f_formation(self, pos1, pos2, look_vector1, look_vector2, threshold=200):
        """
        Check if two positions, each with a looking direction, are in a F-Formation.
        :param pos1: Position in cm.
        :param pos2: Position in cm.
        :param look_vector1:
        :param look_vector2:
        :param threshold: Distance in cm separating the two positions.
        :return:
        """
        v1 = Util.normalize_vector(look_vector1)
        v2 = Util.normalize_vector(look_vector2)
        # distance between the two users
        distance = Util.get_length((pos1[0] - pos2[0], pos1[1] - pos2[1]))

        # if they are close enough to each other
        if distance < threshold:
            diff_vector = (pos2[0] - pos1[0], pos2[1] - pos1[1])
            angle1 = abs(math.degrees(self.angle(v1, diff_vector)))
            angle2 = abs(math.degrees(self.angle(v2, (-diff_vector[0], -diff_vector[1]))))

            if angle1 > 90 or angle2 > 90 or angle1 - angle2 > 80:
                return 1

            angle_similarity = 1 / (0.2 + abs(angle1 - angle2))
            average_angle = abs((angle1 + angle2) / 2)
            #print "similarity : " + str(angle_similarity)
            #print "average    : " + str(average_angle)

            return -1
        else:
            return -1

    def update_time_frame(self, interval):
        """
        Called by the publisher time_frame to update the visualization to the new interval.
        :param interval: (start, end): new interval start and end as list
        """

        # delete old line nodes
        for i, node in enumerate(self.f_formation_nodes):
            node.unlink()

        # update f-formation positions (a formation has [time, duration, user1, user2])
        for i, formation in enumerate(self.f_formations):
            duration = formation[1]
            start = formation[0] - duration
            end = formation[0]
            user_1 = formation[2]
            user_2 = formation[3]
            user_1_start = self._value_to_pixel(User.users[user_1].get_head_position_averaged(
                int(start/global_values.time_step_size))[0], self.height, global_values.x_range)
            user_1_end = self._value_to_pixel(User.users[user_1].get_head_position_averaged(
                int(end/global_values.time_step_size))[0], self.height, global_values.x_range)
            user_2_start = self._value_to_pixel(User.users[user_2].get_head_position_averaged(
                int(start/global_values.time_step_size))[0], self.height, global_values.x_range)
            user_2_end = self._value_to_pixel(User.users[user_2].get_head_position_averaged(
                int(end/global_values.time_step_size))[0], self.height, global_values.x_range)

            user_color_1 = Util.get_user_color_as_hex(user_1, 1)
            user_color_2 = Util.get_user_color_as_hex(user_2, 1)

            stroke = 3

            if start <= interval[0] < end:
                start_pos = 0
                if end >= interval[1]:
                    length = self.width
                else:
                    length = self._value_to_pixel(end, self.width, interval)

                self.f_formation_nodes.append(
                    libavg.LineNode(parent=self, strokewidth=stroke, color=global_values.COLOR_FOREGROUND,
                                    pos1=(start_pos, user_1_start), pos2=(start_pos + length, user_1_end)))
                self.f_formation_nodes.append(
                    libavg.LineNode(parent=self, strokewidth=stroke, color=global_values.COLOR_FOREGROUND,
                                    pos1=(start_pos, user_2_start), pos2=(start_pos + length, user_2_end)))
                self.f_formation_nodes.append(
                    libavg.LineNode(parent=self, strokewidth=stroke, color=global_values.COLOR_FOREGROUND,
                                    pos1=(start_pos, user_1_start), pos2=(start_pos, user_2_start)))
                self.f_formation_nodes.append(
                    libavg.LineNode(parent=self, strokewidth=stroke, color=global_values.COLOR_FOREGROUND,
                                    pos1=(start_pos + length, user_1_end), pos2=(start_pos + length, user_2_end)))

            elif end > interval[0] and start <= interval[1]:
                start_pos = self._value_to_pixel(start, self.width, interval)
                length = self._value_to_pixel(end - start + interval[0], self.width, interval)
                if end >= interval[1]:
                    length -= self._value_to_pixel(end - interval[1] + interval[0], self.width, interval)

                self.f_formation_nodes.append(
                    libavg.LineNode(parent=self, strokewidth=stroke, color=global_values.COLOR_FOREGROUND,
                                    pos1=(start_pos, user_1_start), pos2=(start_pos + length, user_1_end)))
                self.f_formation_nodes.append(
                    libavg.LineNode(parent=self, strokewidth=stroke, color=global_values.COLOR_FOREGROUND,
                                    pos1=(start_pos, user_2_start), pos2=(start_pos + length, user_2_end)))
                self.f_formation_nodes.append(
                    libavg.LineNode(parent=self, strokewidth=stroke, color=global_values.COLOR_FOREGROUND,
                                    pos1=(start_pos, user_1_start), pos2=(start_pos, user_2_start)))
                self.f_formation_nodes.append(
                    libavg.LineNode(parent=self, strokewidth=stroke, color=global_values.COLOR_FOREGROUND,
                                    pos1=(start_pos + length, user_1_end), pos2=(start_pos + length, user_2_end)))

            # simple rectangle for f-formations
            # self.f_formation_nodes.append(libavg.RectNode(parent=self, strokewidth=1, color=user_color_1,
            #                                               pos=(start_pos, user_1_start), size=(length, -pos_diff)))

    def dot_product(self, v1, v2):
        return sum((a * b) for a, b in zip(v1, v2))

    def length(self, v):
        return math.sqrt(self.dot_product(v, v))

    def angle(self, v1, v2):
        return math.acos(self.dot_product(v1, v2) / (self.length(v1) * self.length(v2)))

    def _value_to_pixel(self, value, max_px, interval):
        """
        calculate pixel position for f-formation position
        """
        a = (interval[1] - interval[0]) / max_px
        return value / a - interval[0] / a
