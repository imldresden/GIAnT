import Util
import math
import libavg
import User


class F_Formations(libavg.DivNode):

    def __init__(self, parent, **kwargs):
        super(F_Formations, self).__init__(**kwargs)
        self.registerInstance(self, parent)

        self.f_duration = 5000          # duration of f-formation in seconds
        self.f_formations = []          # contains all detected f_formation nodes

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
        distance = Util.get_length((pos1[0] - pos2[0], pos1[1] - pos2[1]))
        if distance < threshold:
            print "dist < thre"
            diff_vector = (pos2[0] - pos1[0], pos2[1] - pos1[1])
            angle1 = self.angle(v1, diff_vector)
            angle2 = self.angle(v2, (-diff_vector[0], -diff_vector[1]))
            if abs(angle1) > math.pi / 2 or abs(angle2) > math.pi / 2 or abs(angle1 - angle2) > 80:
                print math.pi
                return None

            angle_similarity = 1 / (0.2 + abs(angle1 - angle2))
            average_angle = abs((angle1 + angle2) / 2)
            print "similarity : " + str(angle_similarity)
            print "average    : " + str(average_angle)

            return 20 / Util.get_length((pos1[0] + 100 * v1[0] - pos2[0] + 100 * v2[0], pos1[1] + 100 * v1[1] - pos2[1] + 100 * v2[1])) * angle_similarity

        else:
            return None

    def update_time_frame(self, interval):
        """
        Called by the publisher time_frame to update the visualization to the new interval.
        :param interval: (start, end): new interval start and end as list
        """

        # create tuple of users to check against existing f-formation
        user_list = []
        for i in range(len(User.users)):
            for j in range(len(User.users)):
                if j > i:
                    user_list.append((i, j))

        # go trough time in time steps half the defined f-formation duration
        t = interval[0]
        while t <= interval[1]:

            # WIP
            # p1 = user_list
            # self.check_for_f_formation(p1, p2, v1, v2)

            # increase time step
            t += self.f_duration / 2

    def dot_product(self, v1, v2):
        return sum((a * b) for a, b in zip(v1, v2))

    def length(self, v):
        return math.sqrt(self.dot_product(v, v))

    def angle(self, v1, v2):
        return math.acos(self.dot_product(v1, v2) / (self.length(v1) * self.length(v2)))
