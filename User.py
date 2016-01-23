import database
import global_values

users = []


class User:
    head_positions = []
    head_positions_integral = []
    viewpoints = []
    touches = []
    head_times = []
    index = -1

    def addHeadPosition(self, position):
        self.head_positions.append(position)

    def clearHeadPositions(self):
        self.head_positions = []

    def addViewpoint(self, point):
        self.viewpoints.append(point)

    def get_head_position_averaged(self, index):
        count = min(global_values.averaging_count, len(self.head_positions_integral) - index - 1)
        integral = self.head_positions_integral
        index = min(max(0, index), len(integral) - 1)
        if count == 0:
            count = 1

        head_position = [(integral[index + count][0] - integral[index][0]) / count,
                         (integral[index + count][1] - integral[index][1]) / count,
                         (integral[index + count][2] - integral[index][2]) / count,
                         integral[index + count][3]]
        return head_position

    def clearViewpoints(self):
        self.viewpoints = []

    def __init__(self, index):
        self.index = index - 1

        self.head_positions = database.get_head_positions(index)
        self.head_positions_integral = database.get_head_positions_integral(index)
        self.head_times = []
        for head_position in self.head_positions:
            self.head_times.append(head_position[3])
        self.viewpoints = database.get_view_points(index)

        self.touches = database.get_touch_positions(index)

        users.append(self)
