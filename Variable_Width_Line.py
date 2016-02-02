#!/usr/bin/env python

from libavg import player, avg
import Draw
import random
import Util
import global_values


class Variable_Width_Line:
    points = []
    widths = []
    opacities = []

    def __init__(self, points, widths, opacities, userid, parent):
        self.id = random.randint(0, 10000000)
        self.points = points
        self.widths = widths
        self.opacities = opacities
        self.color = Util.get_user_color_as_hex(userid, 1)
        self.__genGradient()

        self.node = avg.MeshNode(parent=parent, blendmode="add")
        self.node.setBitmap(self.gradientBmp)
        self.__genMesh()

    def set_values(self, points, widths, opacities):
        self.points = points
        self.widths = widths
        self.opacities = opacities
        self.__genMesh()

    def __genMesh(self):
        vertexes = []
        texcoords = [(0.1, 0), (0.1, 1)]
        triangles = []

        for i in range(len(self.points)):
            p2 = self.points[i]
            t2 = self.widths[i]
            if i < 1:
                p1 = (self.points[0][0] - (self.points[1][0] - self.points[0][0]), self.points[1][0])
                p3 = self.points[i + 1]
                t1 = self.widths[0]
                t3 = self.widths[i + 1]
            else:
                p1 = self.points[i - 1]
                t1 = self.widths[i - 1]
                if i >= len(self.points) - 1:
                    p3 = (2 * self.points[i][0] - self.points[i - 1][0], 2 * self.points[i][1] - self.points[i - 1][1])
                    t3 = self.widths[i]
                else:
                    p3 = self.points[i + 1]
                    t3 = self.widths[i + 1]
            linepos = Draw.calculate_line_intersection(p1, p2, p3, t1, t2, t3)

            vertexes.append(linepos[0])
            vertexes.append(linepos[1])
            texx = max(1.0/256.0,min(255.0 / 256.0, pow(self.opacities[i], 1) * 2))
            texcoords.append((texx, 0))
            texcoords.append((texx, 1))
            triangles.append((i * 2, i * 2 + 1, i * 2 + 2))
            triangles.append((i * 2 + 1, i * 2 + 2, i * 2 + 3))

        vertexes.insert(0, vertexes[1])
        vertexes.insert(0, vertexes[1])
        self.node.vertexcoords = vertexes
        self.node.texcoords = texcoords
        self.node.triangles = triangles

    def __genGradient(self):
        canvas_id = str("gradient " + str(self.id) + self.color)
        if hasattr(self, 'canvas'):
            self.canvas = player.deleteCanvas(canvas_id)
        self.canvas = player.createCanvas(id=canvas_id, size=(256, 1))
        for x in range(256):
            opacity = float(x) / 256.0
            avg.LineNode(pos1=(x + 0.5, -1), pos2=(x + 0.5, 2), color=self.color, opacity=opacity, parent=self.canvas.getRootNode())
        self.canvas.render()
        self.gradientBmp = self.canvas.screenshot()
