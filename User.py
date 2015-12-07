import database

users = []


class User():
    headPositions = []
    viewpoints = []
    touches = []
    id = -1
    color = "#FF0000"

    def addHeadPosition(self, position):
        self.headPositions.append(position)

    def clearHeadPositions(self):
        self.headPositions = []

    def addViewpoint(self, point):
        self.viewpoints.append(point)

    def clearViewpoints(self):
        self.viewpoints = []

    def __init__(self, index, color):
        self.id = index
        self.color = color


        self.headPositions = database.executeQry("SELECT x, y, z FROM normaltable where user = "+str(index)+" AND HEAD=1;", True)
        self.touches = database.executeQry("SELECT x, y FROM normaltable where user = "+str(index)+" AND HEAD=0;", True)

        users.append(self)

