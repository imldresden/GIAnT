#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libavg import avg, app
import variable_width_line


class MyMainDiv(app.MainDiv):
    def onInit(self):
        widths = [1,30,20,10]
        opacities = [0.05,0.1,0.2,0.3]

        line = variable_width_line.VariableWidthLine(color="FFFFFF", parent=self)
        points = [avg.Point2D(10,10), avg.Point2D(100,100), avg.Point2D(200,10), avg.Point2D(300,10)]
        line.set_values(points, widths, opacities)

        line = variable_width_line.VariableWidthLine(color="FFFFFF", parent=self)
        points = [avg.Point2D(10, 250), avg.Point2D(100, 150), avg.Point2D(200, 250), avg.Point2D(300,250)]
        line.set_values(points, widths, opacities)

        line = variable_width_line.VariableWidthLine(color="FFFFFF", parent=self)
        points = [avg.Point2D(10, 300), avg.Point2D(100, 340), avg.Point2D(200, 350), avg.Point2D(300,350)]
        line.set_values(points, widths, opacities)

        line = variable_width_line.VariableWidthLine(color="FFFFFF", parent=self)
        points = [avg.Point2D(10, 400), avg.Point2D(100, 410), avg.Point2D(200, 450), avg.Point2D(300, 450)]
        line.set_values(points, widths, opacities)

app.App().run(MyMainDiv())

