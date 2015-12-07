from libavg import app
import libavg
import User
import Visualization


class MainDrawer(app.MainDiv):

    def onInit(self):
        for userid in range(1, 5):
            user = User.User(userid, "#FF0000")
        Visualization.Visualization(self, (100, 100), (100, 100))


    def onFrame(self):
        print "frame"
        pass

    def drawLine(self, p1, p2, color, thickness):
        return libavg.LineNode(pos1=p1, pos2=p2, color=color, strokewidth=thickness, parent=self)
