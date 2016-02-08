import database
import global_values

users = []


class User:
    head_positions = []
    head_positions_integral = []
    head_orientations_integral = []
    viewpoints = []
    touches = []
    head_times = []
    index = -1
    selected = True

    def addHeadPosition(self, position):
        self.head_positions.append(position)

    def clearHeadPositions(self):
        self.head_positions = []

    def addViewpoint(self, point):
        self.viewpoints.append(point)

    def get_head_position_averaged(self, index):
        count = min(global_values.averaging_count, len(self.head_positions_integral) - index - 1)
        integral = self.head_positions_integral
        if count <= 0:
            count = 1
        index = min(max(0, index), len(integral) - count - 1)

        head_position = [(integral[index + count][0] - integral[index][0]) / count,
                         (integral[index + count][1] - integral[index][1]) / count,
                         (integral[index + count][2] - integral[index][2]) / count,
                         integral[index + count][3]]
        return head_position

    def get_head_orientation_averaged(self, index):
        count = min(global_values.averaging_count, len(self.head_orientations_integral) - index - 1)
        integral = self.head_orientations_integral
        if count <= 0:
            count = 1
        index = min(max(0, index), len(integral) - count - 1)

        head_orientation = [(integral[index + count][0] - integral[index][0]) / count,
                            (integral[index + count][1] - integral[index][1]) / count,
                            (integral[index + count][2] - integral[index][2]) / count,
                            integral[index + count][3]]
        return head_orientation

    def get_view_point_averaged(self, index):
        count = min(global_values.averaging_count, len(self.viewpoints_integral) - index - 1)
        integral = self.viewpoints_integral
        if count <= 0:
            count = 1
        index = min(max(0, index), len(integral) - count - 1)

        view_point = [(integral[index + count][0] - integral[index][0]) / count,
                      (integral[index + count][1] - integral[index][1]) / count,
                      integral[index + count][2]]
        return view_point

    def clearViewpoints(self):
        self.viewpoints = []

    def __init__(self, index):
        self.index = index - 1

        # self.head_positions = database.get_head_positions(index)
        self.head_positions_integral = database.get_head_positions_integral(index)
        # self.head_times = []
        # for head_position in self.head_positions:
        #     self.head_times.append(head_position[3])

        self.head_orientations_integral = database.get_head_orientations_integral(index)

        self.viewpoints_integral = database.get_view_points_integral(index)

        self.touches = database.get_touch_positions(index)

        users.append(self)
