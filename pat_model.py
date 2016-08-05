# -*- coding: utf-8 -*-

import time
import sqlite3
import math
from libavg import avg, player

player.loadPlugin("pyglm")

wall_width = 4.90
wall_height = 2.06
pos_range = [(-0.5,0,0.5), (5.5,2.5,2.5)]  # User head position minimum and maximum
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


# Converts time from csv format to float seconds since 1970.
def csvtime_to_float(date, csv_time):
    time_str = date + " " + csv_time
    (time_str, millisecs_str) = time_str.split(".")
    time_struct = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    millisecs = int(millisecs_str)
    return time.mktime(time_struct) + float(millisecs) / 1000


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

class HeadData(object):
    def __init__(self):
        self.userid = None
        self.pos = None
        self.rotation = None
        self.timestamp = None
        self.pos_prefix_sum = None

    def as_list(self):
        return (self.userid,
                self.pos[0], self.pos[1], self.pos[2],
                self.rotation[0], self.rotation[1], self.rotation[2],
                self.timestamp,
                self.pos_prefix_sum[0], self.pos_prefix_sum[1], self.pos_prefix_sum[2])

    def calc_sums(self, prev_data):
        if prev_data:
            self.pos_prefix_sum = (
                prev_data.pos_prefix_sum[0] + self.pos[0],
                prev_data.pos_prefix_sum[1] + self.pos[1],
                prev_data.pos_prefix_sum[2] + self.pos[2])
        else:
            self.pos_prefix_sum = self.pos

    def calc_wall_viewpoint(self):
        yaw_quat = pyglm.quat.fromAxisAngle((0,1,0), self.rotation[0])
#        pitch_quat = pyglm.quat.fromAxisAngle((1,0,0), self.rotation[1])
#        roll_quat = pyglm.quat.fromAxisAngle((0,0,1), self.rotation[2])
        q = yaw_quat #* pitch_quat * roll_quat
        head_dir = q*pyglm.vec3(0,0,1)

        viewpt3d = line_plane_intersect(self.pos, head_dir, (0,0,0), (0,0,1))
        if viewpt3d is not None:
            self.wall_viewpoint = avg.Point2D(viewpt3d.x, viewpt3d.y)
        else:
            self.wall_viewpoint = avg.Point2D(0,0)

    @classmethod
    def from_csv(cls, csv_record, date):
        head_data = HeadData()
        head_data.timestamp = csvtime_to_float(date, csv_record[0])
        head_data.userid = eval(csv_record[1])-1
        head_data.pos = list(eval(csv_record[2]))
        # pos is in Meters, origin is lower left corner of the wall.
        # In the CSV file:
        #   If facing the wall, x points left, y up, z into the wall
        # In the DB:
        #   If facing the wall, x points right, y up, z away from the wall
        head_data.pos[0] = -head_data.pos[0]
        head_data.pos[2] = -head_data.pos[2]
        # Rotation is yaw, pitch, roll, origin is facing wall.
        head_data.rotation = eval(csv_record[3])
        return head_data

    @classmethod
    def from_list(cls, head_list):
        head_data = HeadData()
        head_data.userid = head_list[0]
        head_data.pos = head_list[1], head_list[2], head_list[3]
        head_data.rotation = head_list[4], head_list[5], head_list[6]
        head_data.timestamp = head_list[7]
        head_data.pos_prefix_sum = head_list[8], head_list[9], head_list[10]
        head_data.calc_wall_viewpoint()
        return head_data

    @classmethod
    def create_interpolated(cls, data1, data2, cur_time):

        def interpolate(x1, x2, ratio):
            return x1 * ratio + x2 * (1 - ratio)

        if data1 is None:
            return data2
        else:
            part = (cur_time - data1.timestamp) / (data2.timestamp - data1.timestamp)
            assert(data1.userid == data2.userid)
            head_data = HeadData()
            head_data.timestamp = cur_time
            head_data.userid = data1.userid
            head_data.pos = [interpolate(data1.pos[0], data2.pos[0], part),
                    interpolate(data1.pos[1], data2.pos[1], part),
                    interpolate(data1.pos[2], data2.pos[2], part)]
            head_data.rotation = [interpolate(data1.rotation[0], data2.rotation[0], part),
                    interpolate(data1.rotation[1], data2.rotation[1], part),
                    interpolate(data1.rotation[2], data2.rotation[2], part)]
            return head_data


class Touch(object):
    def __init__(self):
        self.userid = None
        self.pos = avg.Point2D()
        self.timestamp = None
        self.duration = None


    @classmethod
    def from_list(cls, session, touch_list):
        touch = Touch()
        touch.userid = touch_list[0]
        touch.pos = avg.Point2D(touch_list[1], touch_list[2])
        touch.timestamp = touch_list[3] - session.start_time
        touch.duration = touch_list[4]
        return touch


class User(object):
    def __init__(self, session, userid):
        self.userid = userid
        self.__duration = session.duration

        head_data_list = execute_qry("SELECT user, x, y, z, pitch, yaw, roll, time, x_sum, y_sum, z_sum "
                          "FROM head WHERE user = " + str(userid) +
                          " GROUP BY time ORDER BY time;", True)
        self.__head_data = [HeadData.from_list(head_list) for head_list in head_data_list]


        touch_data_list = execute_qry("SELECT user, x, y, time, duration "
                                     "FROM touch WHERE user = " + str(userid) +
                                     " GROUP BY time ORDER BY time;", True)
        self.__touches = [Touch.from_list(session, touch_list) for touch_list in touch_data_list]

    def get_num_states(self):
        return len(self.__head_data)

    def get_viewpoint(self, cur_time):
        i = self.__time_to_index(cur_time)
        return self.__head_data[i].wall_viewpoint

    def get_head_position(self, cur_time):
        i = self.__time_to_index(cur_time)
        return self.__head_data[i].pos

    def get_head_orientation(self, cur_time):
        i = self.__time_to_index(cur_time)
        return self.__head_data[i].rotation

    def get_head_position_averaged(self, cur_time, smoothness):

        i = self.__time_to_index(cur_time)
        start_integral = self.__head_data[max(0, i - smoothness/2)].pos_prefix_sum
        end_integral = self.__head_data[min(len(self.__head_data)-1, i + int((smoothness+1)/2))].pos_prefix_sum
        head_position = [(end_integral[0] - start_integral[0]) / smoothness,
                         (end_integral[1] - start_integral[1]) / smoothness,
                         (end_integral[2] - start_integral[2]) / smoothness]
        return head_position

    def get_touches(self, start_time, end_time):
        touches = [touch for touch in self.__touches if start_time <= touch.timestamp < end_time]
        return touches

    def get_view_point_averaged(self, cur_time, smoothness):
        # TODO: Unused, untested
        i = self.__time_to_index(cur_time)
        count = min(smoothness, len(self.__viewpoints_integral) - i - 1)
        integral = self.__viewpoints_integral
        if count <= 0:
            count = 1
        i = min(max(0, i), len(integral) - count - 1)

        view_point = [(integral[i + count][0] - integral[i][0]) / count,
                      (integral[i + count][1] - integral[i][1]) / count]
        return view_point

    def __time_to_index(self, t):
        return int(t * len(self.__head_data) / self.__duration)


class Session(object):
    def __init__(self, data_dir, optitrack_filename, touch_filename, video_filename, date,
            video_start_time, video_time_offset, num_users):
        self.data_dir = data_dir
        self.optitrack_filename = optitrack_filename
        self.touch_filename = touch_filename
        self.video_filename = video_filename
        self.date = date
        self.num_users = num_users

        time_str = date + " " + video_start_time
        time_struct = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        self.video_start_time = time.mktime(time_struct) + video_time_offset

        self.start_time = execute_qry("SELECT min(time) FROM head;", True)[0][0]
        self.duration = execute_qry("SELECT max(time) FROM head;", True)[0][0] - self.start_time

        self.__users = []
        for userid in range(0, num_users):
            self.__users.append(User(self, userid))

    def get_video_time_offset(self):
        return self.start_time - self.video_start_time

    @property
    def users(self):
        return self.__users


def create_session():
    return Session(
        data_dir="Study Data/Session 3",
        optitrack_filename="optitrack_Beginner's Village15-24_17-03-2016_log.csv",
        touch_filename="touch_Beginner's Village15-24_17-03-2016_log.csv",
        video_filename="2016.03.17-151215.avi",
        date="2016-03-17",
        video_start_time="15:12:15",
        video_time_offset=0.3,
        num_users=4
    )
