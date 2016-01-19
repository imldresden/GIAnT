#!/usr/bin/env python

from libavg import player, avg
import Draw


class Variable_Width_Line:
    points = []
    widths = []
    color = 'FF0000'

    def __init__(self, points, widths, color, parent):
        self.points = points
        self.widths = widths
        self.color = color
        self.__genGradient()

        self.node = avg.MeshNode(parent=parent, blendmode="add")
        self.node.setBitmap(self.gradientBmp)
        self.__genMesh()

    def set_points_and_widths(self, points, widths):
        self.points = points
        self.widths = widths
        self.__genGradient()
        self.node.setBitmap(self.gradientBmp)
        self.__genMesh()

    def __genMesh(self):
        vertexes = []
        texcoords = [(0.1, 0), (0.1, 0)]
        triangles = []
        for i in range(len(self.points)):
            p2 = self.points[i]
            t2 = self.widths[i]
            if (i < 1):
                p1 = (self.points[0][0] - (self.points[1][0] - self.points[0][0]), self.points[1][0])
                p3 = self.points[i + 1]
                t1 = self.widths[0]
                t3 = self.widths[i + 1]
            else:
                p1 = self.points[i - 1]
                t1 = self.widths[i - 1]
                if (i >= len(self.points) - 1):
                    p3 = (2 * self.points[i][0] - self.points[i - 1][0], self.points[i - 1][1])
                    t3 = self.widths[i]
                else:
                    p3 = self.points[i + 1]
                    t3 = self.widths[i + 1]
            linepos = Draw.calculate_line_intersection(p1, p2, p3, t1, t2, t3)

            vertexes.append(linepos[0])
            vertexes.append(linepos[1])
            texx = (i + 1) / float(len(self.widths) - 1)
            texcoords.append((texx, 0))
            texcoords.append((texx, 0))
            triangles.append((i * 2, i * 2 + 1, i * 2 + 2))
            triangles.append((i * 2 + 1, i * 2 + 2, i * 2 + 3))

        vertexes.insert(0, vertexes[1])
        vertexes.insert(0, vertexes[1])
        self.node.vertexcoords = vertexes
        self.node.texcoords = texcoords
        self.node.triangles = triangles

    def __genGradient(self):
        canvas_id = str("gradient " + self.color)
        if hasattr(self, 'canvas'):
            self.canvas = player.deleteCanvas(canvas_id)
        self.canvas = player.createCanvas(id=canvas_id, size=(len(self.widths) - 1, 1))
        for x in range(len(self.widths)):
            if self.widths[x] <= 0:
                opacity = 1
            else:
                opacity = 3 / (self.widths[x])
            opacity += 0.0
            avg.LineNode(pos1=(x + 0.5, -0.5), pos2=(x + 0.5, 1.5), color=self.color, opacity=opacity, parent=self.canvas.getRootNode())
        self.canvas.render()
        self.gradientBmp = self.canvas.screenshot()
