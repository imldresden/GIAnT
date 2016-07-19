# -*- coding: utf-8 -*-
# !/usr/bin/env python

from libavg import player, avg
import random
import math
import util


def calculate_line_intersection(p1, p2_selected, p3, thickness1, thickness2_selected, thickness3):
    thickness1 *= 0.5
    thickness2_selected *= 0.5
    thickness3 *= 0.5
    vector_1 = (p2_selected[0] - p1[0], p2_selected[1] - p1[1])
    vector_2 = (p3[0] - p2_selected[0], p3[1] - p2_selected[1])

    vector_length_1 = math.sqrt(vector_1[0] * vector_1[0] + vector_1[1] * vector_1[1])
    vector_length_2 = math.sqrt(vector_2[0] * vector_2[0] + vector_2[1] * vector_2[1])
    try:
        normalized_vector_1 = (vector_1[0] / vector_length_1, vector_1[1] / vector_length_1)
        normalized_vector_2 = (vector_2[0] / vector_length_2, vector_2[1] / vector_length_2)
    except:
        normalized_vector_1 = (0, 1)
        normalized_vector_2 = (0, 1)

    left_1 = (p1[0] - normalized_vector_1[1] * thickness1, p1[1] + normalized_vector_1[0] * thickness1)
    left2_1 = (p2_selected[0] - normalized_vector_1[1] * thickness2_selected,
               p2_selected[1] + normalized_vector_1[0] * thickness2_selected)
    left2_2 = (p2_selected[0] - normalized_vector_2[1] * thickness2_selected,
               p2_selected[1] + normalized_vector_2[0] * thickness2_selected)
    left_3 = (p3[0] - normalized_vector_2[1] * thickness3, p3[1] + normalized_vector_2[0] * thickness3)

    right_1 = (p1[0] + normalized_vector_1[1] * thickness1, p1[1] - normalized_vector_1[0] * thickness1)
    right2_1 = (p2_selected[0] + normalized_vector_1[1] * thickness2_selected,
                p2_selected[1] - normalized_vector_1[0] * thickness2_selected)
    right2_2 = (p2_selected[0] + normalized_vector_2[1] * thickness2_selected,
                p2_selected[1] - normalized_vector_2[0] * thickness2_selected)
    right_3 = (p3[0] + normalized_vector_2[1] * thickness3, p3[1] - normalized_vector_2[0] * thickness3)

    intersection_point_1 = util.line_intersection((left_1, left2_1), (left2_2, left_3))
    intersection_point_2 = util.line_intersection((right_1, right2_1), (right2_2, right_3))

    return [intersection_point_1, intersection_point_2]


class VariableWidthLine:
    points = []
    widths = []
    opacities = []

    def __init__(self, color, parent):
        self.color = color
        self.__genGradient()

        self.node = avg.MeshNode(parent=parent, blendmode="add")
        self.node.setBitmap(self.gradientBmp)

    def set_values(self, points, widths, opacities):
        self.points = points
        self.widths = widths
        self.opacities = opacities
        self.__genMesh()

    def __genMesh(self):
        vertexes = []
        texcoords = [(0.1, 0), (0.1, 1)]
        triangles = []
        if self.widths == None or len(self.widths)!=len(self.points):
            self.widths = []
            self.widths = self.widths + [3]*(len(self.points)-len(self.widths))
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
                    p3 = (2 * self.points[i][0] - self.points[i - 1][0],
                          2 * self.points[i][1] - self.points[i - 1][1])
                    t3 = self.widths[i]
                else:
                    p3 = self.points[i + 1]
                    t3 = self.widths[i + 1]
            linepos = calculate_line_intersection(p1, p2, p3, t1, t2, t3)

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
        canvas = player.createCanvas(id="gradient", size=(256, 1))
        for x in range(256):
            opacity = float(x) / 256.0
            avg.LineNode(pos1=(x + 0.5, -1), pos2=(x + 0.5, 2), color=self.color, opacity=opacity,
                         parent=canvas.getRootNode())
        canvas.render()
        self.gradientBmp = canvas.screenshot()
        player.deleteCanvas("gradient")
