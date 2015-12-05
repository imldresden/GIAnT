import libavg
from libavg import app, avg


import FileLoader
import database
import Visualizations.VerticalLines

class MainDrawer(app.MainDiv):

    canvasObjects = []
    maxTime = database.executeQry("SELECT max(time) from normaltable;", True)[0][0]
    visualization = Visualizations.VerticalLines.VerticalLines()
    resolution = (1000, 1000)
    zoomscale = 0.1
    zoom = 1
    currentZoom = 1
    offset = 0
    currentOffset = 0
    def onInit(self):
        self.canvasObjects.append(libavg.RectNode(pos=(0, 0), size=(1000, 1000), color=(255, 255, 255),
                                                  fillcolor=(255, 255, 255), strokewidth=10000,  parent=self))
        self.drawCircle(app.instance._resolution/2, (255,255,255), 2000)
        MainDrawer.resolution = app.instance._resolution
        self.timeframe = (FileLoader.minTime, FileLoader.maxTime)
        database.fetchNormData()
        app.keyboardmanager.bindKeyDown(text='+', handler=self.zoomIn,
                help='zoomIn')
        app.keyboardmanager.bindKeyDown(text='-', handler=self.zoomOut,
                help='zoomIn')
        app.keyboardmanager.bindKeyDown(text='2', handler=self.down,
                help='zoomIn')
        app.keyboardmanager.bindKeyDown(text='8', handler=self.up,
                help='zoomIn')
        #self.subscribe(avg.KEYDOWN, self.onMouse)
        #avg.Publisher.subscribe(libavg.avg.KEYDOWN, self.onMouse)

        # app.keyboardmanager.bindKeyDown('+', self.zoomIn, 'zoom in')
        # app.keyboardmanager.bindKeyDown('-', self.zoomIn, 'zoom out')
        pass

    def drawCircle(self, pos, color, radius):
        libavg.CircleNode(pos=pos, r=radius, fillcolor=color, fillopacity=1, parent=self)

    def drawPolyLine(self, points, color, thickness, lineindex=0):
        if(len(self.canvasObjects)>lineindex):
            self.canvasObjects[lineindex].pos = points
        else:
            self.canvasObjects.append(libavg.PolyLineNode(pos=points, color=color, strokewidth=thickness, linejoin="bevel", parent=self))

    def drawLine(self, p1, p2, color, thickness):
        self.canvasObjects.append(libavg.LineNode(pos1=p1, pos2=p2, color=color, strokewidth=thickness, parent=self))

    def clear(self):
        for item in self.canvasObjects:
            app.MainDiv.removeChild(self, item)

        self.canvasObjects = []

    def onFrame(self):
        smoothness = 0.9
        self.currentZoom = (self.currentZoom*smoothness + self.zoom*(1-smoothness))
        self.currentOffset = (self.currentOffset*smoothness + self.offset*(1-smoothness))

        #self.clear()
        self.visualization.drawFrame(self, self.currentZoom, self.currentOffset)
        pass

    def up(self):
        try:
            self.offset -= 1/(self.zoom-1)
        except:
            None

    def down(self):
        try:
            self.offset += 1/(self.zoom-1)
        except:
            None

    def zoomIn(self):
        print (2-self.zoom)*self.zoomscale
        self.zoom+=(1.5-self.zoom)*self.zoomscale


    def zoomOut(self):
        strength = (1.5-self.zoom)*self.zoomscale
        self.zoom -= self.zoom/((1/strength)+1)

    def onMouse(self, event):
        print event


app.App().run(MainDrawer(), app_resolution='1920x1000')
