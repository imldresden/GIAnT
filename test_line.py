#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libavg import avg, app
import variable_width_line


class MyMainDiv(app.MainDiv):
    def onInit(self):
        self.widths = [1,30,30,10]
        self.opacities = [0.05,0.1,0.2,0.3]

        points = [avg.Point2D(10, 10), avg.Point2D(100, 100), avg.Point2D(120, 10), avg.Point2D(200, 10)]
        self.__create_line(points)

        points = [avg.Point2D(10, 250), avg.Point2D(100, 150), avg.Point2D(200, 250), avg.Point2D(300, 250)]
        self.__create_line(points)

        points = [avg.Point2D(10, 300), avg.Point2D(100, 340), avg.Point2D(110, 380), avg.Point2D(120, 340)]
        self.__create_line(points)

        points = [avg.Point2D(10, 400), avg.Point2D(100, 410), avg.Point2D(200, 450), avg.Point2D(300, 450)]
        self.__create_line(points)

    def __create_line(self, points):
        line = variable_width_line.VariableWidthLine(color="FFFFFF", parent=self)
        line.set_values(points, self.widths, self.opacities)
        avg.PolyLineNode(pos=points, color="FF0000", parent=self)


app.App().run(MyMainDiv())

