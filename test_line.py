#!/usr/bin/env python
# -*- coding: utf-8 -*-
# GIAnT Group Interaction Analysis Toolkit
# Copyright (C) 2017 Interactive Media Lab Dresden
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from libavg import avg, app, player
player.loadPlugin("plots")


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
        line = plots.VWLineNode(color="FFFFFF", parent=self)
        line.setValues(points, self.widths, self.opacities)
        avg.PolyLineNode(pos=points, color="FF0000", parent=self)


app.App().run(MyMainDiv())

