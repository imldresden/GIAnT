# -*- coding: utf-8 -*-
# !/usr/bin/env python

from libavg import player, avg
import math


class VariableWidthLine(avg.MeshNode):
    points = []
    widths = []
    opacities = []

    def __init__(self, color, parent, **kwargs):
        super(VariableWidthLine, self).__init__(**kwargs)
        self.registerInstance(self, parent)
        self.color = color
        self.blendmode = "add"
        self.__genGradient()
        self.setBitmap(self.gradientBmp)

    def set_values(self, points, widths, opacities):
        self.points = points
        self.widths = widths
        self.opacities = opacities
        self.__genMesh()

    def __genMesh(self):

        def calc_tex_coord(opacity):
            return avg.Point2D(max(1.0/256.0,min(255.0 / 256.0, pow(opacity, 1) * 2)), 0)

        vertexes = []
        texcoords = []
        triangles = []

        # First point
        pt0 = self.points[0]
        offset = avg.Point2D(0, self.widths[0]/2)
        pt0_t = pt0 - offset
        pt0_b = pt0 + offset
        vertexes.extend((pt0_t, pt0, pt0_b))
        texcoord = calc_tex_coord(self.opacities[0])
        texcoords.extend((texcoord, texcoord, texcoord))

        for i in range(1, len(self.points)-1):
            pt0 = self.points[i-1]
            pt1 = self.points[i]
            pt2 = self.points[i+1]
            offset = self.widths[i] / 2
            vi = len(vertexes)
            if pt1.y > pt0.y and pt1.y > pt2.y:
                # Current point below both neighbors
                delta = pt1 - pt0
                norm = avg.Point2D(-delta.y, delta.x).getNormalized()
                pt1_bl = pt1 + norm*offset
                delta = pt2 - pt1
                norm = avg.Point2D(-delta.y, delta.x).getNormalized()
                pt1_br = pt1 + norm*offset
                pt1_t = pt1 - (0, offset)

                vertexes.extend((pt1_bl, pt1_t, pt1, pt1_br))
                texcoord = calc_tex_coord(self.opacities[i])
                texcoords.extend((texcoord, texcoord, texcoord, texcoord))
                triangles.append((vi-3, vi+1, vi+2))
                triangles.append((vi-3, vi+2, vi-2))
                triangles.append((vi-2, vi+2, vi-1))
                triangles.append((vi-1, vi+2, vi  ))
                triangles.append((vi,   vi+2, vi+3))
            elif pt1.y < pt0.y and pt1.y < pt2.y:
                # Current point above both neighbors
                delta = pt1 - pt0
                norm = avg.Point2D(-delta.y, delta.x).getNormalized()
                pt1_tl = pt1 - norm*offset
                delta = pt2 - pt1
                norm = avg.Point2D(-delta.y, delta.x).getNormalized()
                pt1_tr = pt1 - norm*offset
                pt1_b = pt1 + (0, offset)

                vertexes.extend((pt1_tl, pt1_tr, pt1, pt1_b))
                texcoord = calc_tex_coord(self.opacities[i])
                texcoords.extend((texcoord, texcoord, texcoord, texcoord))
                triangles.append((vi - 3, vi, vi + 2))
                triangles.append((vi - 3, vi + 2, vi - 2))
                triangles.append((vi - 2, vi + 2, vi - 1))
                triangles.append((vi - 1, vi + 2, vi + 3))
                triangles.append((vi, vi + 1, vi + 2))
            else:
                # Current point has neighbors above and below.
                offset = avg.Point2D(0, self.widths[i] / 2)
                pt1_t = pt1 - offset
                pt1_b = pt1 + offset
                vertexes.extend((pt1_t, pt1, pt1_b))
                texcoord = calc_tex_coord(self.opacities[i])
                texcoords.extend((texcoord, texcoord, texcoord))
                triangles.append((vi-3, vi,   vi+1))
                triangles.append((vi-3, vi+1, vi-2))
                triangles.append((vi-2, vi+1, vi-1))
                triangles.append((vi-1, vi+1, vi+2))

        # Last point
        i = len(self.points)-1
        vi = len(vertexes)
        pt1 = self.points[i]
        offset = avg.Point2D(0, self.widths[i]/2)
        pt1_t = pt1 - offset
        pt1_b = pt1 + offset
        vertexes.extend((pt1_t, pt1, pt1_b))
        texcoord = calc_tex_coord(self.opacities[i])
        texcoords.extend((texcoord, texcoord, texcoord))
        triangles.append((vi - 3, vi, vi + 1))
        triangles.append((vi - 3, vi + 1, vi - 2))
        triangles.append((vi - 2, vi + 1, vi - 1))
        triangles.append((vi - 1, vi + 1, vi + 2))

        self.vertexcoords = vertexes
        self.texcoords = texcoords
        self.triangles = triangles

    def __genGradient(self):
        canvas = player.createCanvas(id="gradient", size=(256, 1))
        for x in range(256):
            opacity = float(x) / 256.0
            avg.LineNode(pos1=(x + 0.5, -1), pos2=(x + 0.5, 2), color=self.color, opacity=opacity,
                         parent=canvas.getRootNode())
        canvas.render()
        self.gradientBmp = canvas.screenshot()
        player.deleteCanvas("gradient")
