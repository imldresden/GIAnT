import User
import libavg
import MainDrawer

class Visualization():
    canvasObjects = []
    size = (100, 100)
    position = (0, 0)
    subdivs = 2000
    parent = 0

    def __init__(self, parent, size, position):
        self.size = size
        self.position = position
        for user in User.users:
            userObjects = []
            for i in range(self.subdivs):
                posindex = int(len(user.headPositions)/float(2000))
                userObjects.append(MainDrawer.MainDrawer.drawLine(parent, user.headPositions[posindex], user.headPositions[posindex+1], 'FF0000', 2))
            self.canvasObjects.append(userObjects)

    def draw(self):

        for user in User.users:
            for point in user.headPositions:
                None

