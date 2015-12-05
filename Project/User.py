import colorsys
from Util import addVectors

users = []


class User:
    dataPoints = []
    headLocations = []
    headDirections = []
    viewPoints = []
    id = -1
    color = colorsys.hsv_to_rgb(0, 1, 1)

    def __init__(self, id):
        users.append(self)
        self.id = int(id)
        self.headDirections = []
        self.headLocations = []
        pass

    def addDataPoint(self, dataPoint):
        self.dataPoints.append(dataPoint)

    def addLocation(self, pos):
        self.headLocations.append(pos)

    def addHeadDirection(self, dir):
        self.headDirections.append(dir)

    def addTouch(self, x, y):
        pass

    def calcViewPoint(self, pos, dir):
        print("TODO: Berechnung noch Quatsch, aber macht trotzdem was^^")
        return addVectors(pos, dir)

    def calcViewPoints(self):
        count = min(len(self.headDirections), len(self.headLocations))
        self.viewPoints = []
        for i in range(0, count):
            self.viewPoints.append(self.calcViewPoint(self.headLocations, self.headDirections))

