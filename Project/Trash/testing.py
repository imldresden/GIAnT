from libavg import avg, app
import random, libavg

class Drawer(app.MainDiv):
    points = []
    polyline = None
    def makePoints(self):
        self.points=[]
        for i in range(0,300000):
            self.points.append((random.randint(0, 1000), random.randint(0, 1000)))

    def onFrame(self):
        self.makePoints()
        self.polyline = self.points

    def onInit(self):
        self.makePoints()
        polyline = libavg.PolyLineNode(pos=self.points, color="ff0000", strokewidth=5, parent=self)
        app.keyboardmanager.bindKeyDown(text='+', handler=self.makePoints,
                help='zoomIn')

app.App().run(Drawer(), app_resolution='1000x1000')