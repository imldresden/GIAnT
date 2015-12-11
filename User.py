import database

users = []


class User:
    head_positions = []
    viewpoints = []
    touches = []
    id = -1
    color = "#FF0000"

    def addHeadPosition(self, position):
        self.head_positions.append(position)

    def clearHeadPositions(self):
        self.head_positions = []

    def addViewpoint(self, point):
        self.viewpoints.append(point)

    def clearViewpoints(self):
        self.viewpoints = []

    def __init__(self, index, color):
        self.id = index
        self.color = color

        self.head_positions = database.get_head_positions(index)
        self.touches = database.get_touch_positions(index)

        users.append(self)
