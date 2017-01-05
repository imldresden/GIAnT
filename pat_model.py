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

import time
import sqlite3
import math
from libavg import avg, player
import glob, os

player.loadPlugin("pyglm")

wall_width = 4.90
wall_height = 2.06
pos_range = [[-0.5,0,0.5], [5.5,2.5,2.5]]  # User head position minimum and maximum
max_time = 0
time_offset = 0
touch_range = [4*1920, 3*1080]
x_wall_range = [0, wall_width]
y_wall_range = [0.4, 0.4+wall_height]


def execute_qry(qry, do_fetch=False):
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.execute(qry)
    if do_fetch:
        data = cur.fetchall()
    con.commit()
    con.close()
    if do_fetch:
        return data


def line_plane_intersect(line_pt, line_dir, plane_pt, plane_normal):
    line_pt = pyglm.vec3(line_pt)
    line_dir = pyglm.vec3(line_dir)
    plane_pt = pyglm.vec3(plane_pt)
    numerator = pyglm.vec3.dot(plane_pt - line_pt, plane_normal)
    denominator = pyglm.vec3.dot(line_dir, plane_normal)
    if math.fabs(denominator) > 0.000000001:
        length = numerator/denominator
        return pyglm.vec3(line_pt + pyglm.vec3(line_dir.getNormalized())*length)
    else:
        return None


class Session(object):
    def __init__(self, session_num, level_num, data_dir, optitrack_filename, touch_filename, video_filename, date,
            video_start_time, video_time_offset, num_users, tool_to_userid, user_pitch_offsets):
        self.session_num = session_num
        self.level_num = level_num
        self.data_dir = data_dir
        self.optitrack_filename = optitrack_filename
        self.touch_filename = touch_filename
        self.video_filename = video_filename
        self.date = date
        self.num_users = num_users
        self.tool_to_userid = tool_to_userid # Maps (Pick, Girder, Lantern, Ladder) to userid.
        # user_pitch_offsets: The recorded pitch data is incorrect by a constant if the subjects didn't wear the
        # helmet correctly.
        self.user_pitch_offsets = user_pitch_offsets

        time_str = date + " " + video_start_time
        time_struct = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        self.video_start_time = time.mktime(time_struct) + video_time_offset


    def load_from_db(self):
        self.start_time = execute_qry(
                "SELECT min(time) FROM head WHERE "+self.__get_level_select()+";", True)[0][0]
        self.duration = execute_qry(
                "SELECT max(time) FROM head WHERE "+self.__get_level_select()+";", True)[0][0] - self.start_time

        self.__users = []
        for userid in range(0, self.num_users):
            self.__users.append(self.__create_user(userid))

    def get_video_time_offset(self):
        return self.start_time - self.video_start_time

    @property
    def users(self):
        return self.__users

    def __create_user(self, userid):
        user = plots.User(userid, self.duration)
        pitch_offset = self.user_pitch_offsets[userid]

        head_data_list = execute_qry("SELECT user, x, y, z, pitch, yaw, roll, time, x_sum, y_sum, z_sum "
                          "FROM head WHERE user = " + str(userid) + " AND " + self.__get_level_select() +
                          " GROUP BY time ORDER BY time;", True)
        for head_list in head_data_list:
            head_data = self.__head_data_from_list(head_list, pitch_offset)
            user.addHeadData(head_data)

        touch_data_list = execute_qry("SELECT user, x, y, time, duration "
                                     "FROM touch WHERE user = " + str(userid) + " AND " + self.__get_level_select() +
                                     " GROUP BY time ORDER BY time;", True)
        for touch_list in touch_data_list:
            touch = self.__touch_data_from_list(self, touch_list)
            user.addTouch(touch)
        return user

    def __head_data_from_list(self, head_list, pitch_offset):

        def calc_wall_viewpoint(head_data):
            yaw_quat = pyglm.quat.fromAxisAngle((0, 1, 0), head_data.rot[0])
            pitch_quat = pyglm.quat.fromAxisAngle((1, 0, 0), head_data.rot[1])
            roll_quat = pyglm.quat.fromAxisAngle((0, 0, 1), head_data.rot[2])
            q = yaw_quat * pitch_quat * roll_quat
            head_dir = q * pyglm.vec3(0, 0, 1)

            viewpt3d = line_plane_intersect(head_data.pos, head_dir, (0, 0, 0), (0, 0, 1))
            if viewpt3d is not None:
                head_data.setWallViewpoint(avg.Point2D(viewpt3d.x, viewpt3d.y))
            else:
                head_data.setWallViewpoint(avg.Point2D(0, 0))

        userid = head_list[0]
        pos = head_list[1], head_list[2]-0.2, head_list[3]
        rot = head_list[4], head_list[5] + pitch_offset, head_list[6]
        timestamp = head_list[7]

        head_data = plots.HeadData(userid, pos, rot, timestamp)
        head_data.posPrefixSum = head_list[8], head_list[9], head_list[10]
        calc_wall_viewpoint(head_data)
        return head_data

    def __touch_data_from_list(self, session, touch_list):
        userid = touch_list[0]
        pos = avg.Point2D(touch_list[1], touch_list[2])
        timestamp = touch_list[3] - session.start_time
        duration = touch_list[4]
        return plots.Touch(userid, pos, timestamp, duration)

    def __get_level_select(self):
        return "session=" + str(self.session_num) + " AND level=" + str(self.level_num)

def create_session(session, level):
    data_dir = "Study Data/Session "+str(session)
    os.chdir(data_dir)
    filenames = glob.glob("optitrack*")
    os.chdir("../..")
    optitrack_filename = filenames[level]
    touch_filename = "touch"+optitrack_filename[9:]
    user_pitch_offsets = [0,0,0,0]
    video_time_offset = 0.0
    if session == 3:
        # Colors: orange, green, blue, purple
        tool_to_userid_table = [
            (0, 1, 2, 3),
            (1, 2, 3, 0)
        ]
        if level == 0:
            user_pitch_offsets = [
                0,
                math.pi / 12,
                0.,
                0.]
        elif level == 1:
            user_pitch_offsets = [
                math.pi * 6/16,
                math.pi * 3/16,
                math.pi * 3/16,
                math.pi * 3/16]
        video_time_offset = 0.3
        video_filename = "2016.03.17-151215_small.mp4"
    elif session == 4:
        tool_to_userid_table = [
            (0, 1, 2, 3),
            (0, 3, 2, 1)
        ]
        video_filename = "2016.03.17-164950.avi"
        if level == 1:
            video_time_offset = 5.0
    elif session == 5:
        tool_to_userid_table = [
            (0, 1, 2, 3),
            (0, 1, 2, 3)
        ]
        video_filename = "2016.03.18-152221.avi"
    else:
        assert False
    date = video_filename[:10].replace(".","-")
    print date
    video_start_time = video_filename[11:13]+":"+video_filename[13:15]+":"+video_filename[15:17]
    return Session(
        session_num=session,
        level_num=level,
        data_dir=data_dir,
        optitrack_filename=optitrack_filename,
        touch_filename=touch_filename,
        video_filename=video_filename,
        date=date,
        video_start_time=video_start_time,
        video_time_offset=video_time_offset,
        num_users=4,
        tool_to_userid=tool_to_userid_table[level],
        user_pitch_offsets=user_pitch_offsets
    )
