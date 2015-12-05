import libavg
import random
import math

from libavg import app, avg, player

numLines = 123
windowWidth = 1024
windowHeight = 768


def addTuples(tuple1, tuple2):
    if(len(tuple1)!=len(tuple2)):
        return tuple1
    newTuple = ()
    for index in range(0, len(tuple1)):
        newTuple += (tuple1[index] + tuple2[index]),
    return newTuple


def toPointTuple(listOfPoints):
    result = []
    for point in listOfPoints:
        result.append(point.position)
    return result


class LinePoint:
    position = (0, 0)

    def __init__(self, pos):
        self.position = pos

    def getPosition(self):
        return self.position

    def addPosition(self, pos):
        oldPos = self.position
        newPos = addTuples(oldPos, pos)
        self.position = newPos


class LineDrawer(app.MainDiv):
    lastPos = (0, 0)
    linePoints = []
    lines = []
    screenRect = 0

    def onDown(self, event):
        self.linePoints[len(self.linePoints)-1].position = event.pos

    def onInit(self):
        self.linePoints.append(LinePoint((self.width/2, self.height/2)))
        self.subscribe(avg.Node.CURSOR_MOTION, self.onDown)

    def onFrame(self):

        if(self.screenRect!=0):
                app.MainDiv.removeChild(self, self.screenRect)
        while (len(self.linePoints)<numLines):
            newAngle = random.randint(0, 360)*math.pi/float(180);
            newLength = random.randint(0, 10)
            newLinePoint = LinePoint((newLength*math.sin(newAngle),newLength*math.cos(newAngle)))
            linePointsSize = len(self.linePoints)-1
            if(linePointsSize >= 0):
                newLinePoint.addPosition(self.linePoints[linePointsSize].getPosition())
            self.linePoints.append(newLinePoint)
        self.screenRect = libavg.RectNode(pos=(0, 0), size=(self.width, self.height), fillopacity=1, fillcolor='FFFFFF', parent=self)
        self.linePoints.__delitem__(0)
        for line in self.lines:
            try:
                app.MainDiv.removeChild(self, line)
                self.lines.remove(line)
            except:
                print("error line 45")

        #for index in range(numLines-2):
            #opacity = index/float(numLines);
            #self.lines.append(libavg.LineNode(
                        # pos1=addTuples(self.linePoints[index].getPosition(), (0, (numLines-index+1)*-1)),
                        # pos2=addTuples(self.linePoints[index+1].getPosition(), (0, (numLines-index)*-1)),
                        # color='FF0000', strokewidth=3, opacity=opacity*0.5, parent=self))
        posi = [(0,0),(0,50),(50,50),(150,50),(150,150)]

        for i in range(0, len(self.linePoints)-1):
            upwards = (-0.5 + i/float(len(self.linePoints)))
            addPoint = (0, -upwards)
            #gridsize = 2
            #self.linePoints[i].position = (math.floor(self.linePoints[i].position[0]/gridsize)*gridsize,
            #                               math.floor(self.linePoints[i].position[1]/gridsize)*gridsize)
            self.linePoints[i].addPosition(addPoint)
        posi2 = toPointTuple(self.linePoints)

        self.lines.append(libavg.PolyLineNode(pos=posi2, strokewidth=1, color='FF00FF', parent=self))
        self.lines.append(libavg.CircleNode(pos=self.linePoints[len(self.linePoints)-1].getPosition(), r=4, fillcolor='0000FF', fillopacity=1, parent=self))

        #print(app.MainDiv.getNumChildren(self))
        self.lines[0].pos1=(0,0)


        #libavg.CircleNode(pos=self.linePoints[numLines-1].getPosition(), r=5, fillcolor='FF0000', parent=self)
        # newPos=(random.randint(2,300), random.randint(2,300))
        # libavg.LineNode(pos1=self.lastPos, pos2=newPos, color='FF0000', parent=self)
        # #libavg.AreaNode(angle=0, pos=(0,0), size=(300,300), color='FFFF00', parent=self)
        # self.lastPos = newPos

app.App().run(LineDrawer(), app_resolution='1900x1000')
