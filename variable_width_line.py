# -*- coding: utf-8 -*-
# !/usr/bin/env python

from libavg import player, avg
import math


def intersect_lines(pt00, pt01, pt10, pt11):
    # Returns intersection of two lines given two points on each line.
    # Line0 is (pt00, pt01), line1 is (pt10, pt11)
    # See https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line
    denom = (pt00.x-pt01.x) * (pt10.y-pt11.y) - (pt00.y-pt01.y) * (pt10.x-pt11.x)
    x = ((pt00.x*pt01.y - pt00.y*pt01.x) * (pt10.x-pt11.x) - (pt00.x-pt01.x) * (pt10.x*pt11.y - pt10.y*pt11.x))/denom
    y = ((pt00.x*pt01.y - pt00.y*pt01.x) * (pt10.y-pt11.y) - (pt00.y-pt01.y) * (pt10.x*pt11.y - pt10.y*pt11.x))/denom
    return avg.Point2D(x,y)


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

        def handle_overlap(pt1, pt0):
            if pt1.x < pt0.x:
                return pt0
            else:
                return pt1

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
            w = self.widths[i] / 2
            vi = len(vertexes)

            delta0 = pt1 - pt0
            offset0 = avg.Point2D(-delta0.y, delta0.x).getNormalized() * w
            delta1 = pt2 - pt1
            offset1 = avg.Point2D(-delta1.y, delta1.x).getNormalized() * w
            texcoord = calc_tex_coord(self.opacities[i])

            slope1 = (pt1.y-pt0.y)/(pt1.x-pt0.x)
            slope2 = (pt2.y-pt1.y)/(pt2.x-pt1.x)
            if math.fabs(slope1-slope2) < 0.03:
                # Near-parallel lines
                pt1_t = pt1 - offset0
                pt1_b = pt1 + offset0
                pt0_t = pt0 - offset0
                pt0_b = pt0 + offset0
                pt1_b = handle_overlap(pt1_b, pt0_b)
                pt1_t = handle_overlap(pt1_t, pt0_t)

                vertexes.extend((pt1_t, pt1, pt1_b))
                texcoords.extend((texcoord, texcoord, texcoord))
                triangles.append((vi - 3, vi, vi + 1))
                triangles.append((vi - 3, vi + 1, vi - 2))
                triangles.append((vi - 2, vi + 1, vi - 1))
                triangles.append((vi - 1, vi + 1, vi + 2))
            elif slope1 < slope2:
                # Curve to the right: Small triangle at top.
                pt1_tl = pt1 - offset0
                pt1_bl = pt1 + offset0
                pt0_b = pt0 + offset0

                pt1_tr = pt1 - offset1
                pt1_br = pt1 + offset1
                pt2_b = pt2 + offset1

                pt1_b = intersect_lines(pt0_b, pt1_bl, pt1_br, pt2_b)
                pt1_b = handle_overlap(pt1_b, pt0_b)

                vertexes.extend((pt1_tl, pt1_tr, pt1, pt1_b))
                texcoords.extend((texcoord, texcoord, texcoord, texcoord))
                triangles.append((vi - 3, vi, vi + 2))
                triangles.append((vi - 3, vi + 2, vi - 2))
                triangles.append((vi - 2, vi + 2, vi - 1))
                triangles.append((vi - 1, vi + 2, vi + 3))
                triangles.append((vi, vi + 1, vi + 2))
            else:
                # Curve to the left: Small triangle at bottom
                pt1_bl = pt1 + offset0
                pt1_tl = pt1 - offset0
                pt0_t = pt0 - offset0

                pt1_br = pt1 + offset1
                pt1_tr = pt1 - offset1
                pt2_t = pt2 - offset1

                pt1_t = intersect_lines(pt0_t, pt1_tl, pt1_tr, pt2_t)
                pt1_t = handle_overlap(pt1_t, pt0_t)

                vertexes.extend((pt1_bl, pt1_t, pt1, pt1_br))
                texcoords.extend((texcoord, texcoord, texcoord, texcoord))
                triangles.append((vi-3, vi+1, vi+2))
                triangles.append((vi-3, vi+2, vi-2))
                triangles.append((vi-2, vi+2, vi-1))
                triangles.append((vi-1, vi+2, vi  ))
                triangles.append((vi,   vi+2, vi+3))

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
