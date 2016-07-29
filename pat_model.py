# -*- coding: utf-8 -*-

import time
import sqlite3
from libavg import avg

wall_width = 490
wall_height = 206
pos_range = [(0,0,0.5), (0,0,2.5)]  # User head position minimum and maximum
max_time = 0
time_offset = 0
x_touch_range = [0, 4*1920]
y_touch_range = [0, 3*1080]
x_wall_range = [0, wall_width]
y_wall_range = [40, 40+wall_height]


def execute_qry(qry, doFetch=False):
    """
    :param qry: the query to execute (string)
    :param doFetch:  whether data should be fetched and returned
    :return:
    """
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.execute(qry)
    if doFetch:
        data = cur.fetchall()
    con.commit()
    con.close()
    if doFetch:
        return data


# Converts time from csv format to float seconds since 1970.
def csvtime_to_float(date, csv_time):
    time_str = date + " " + csv_time
    (time_str, millisecs_str) = time_str.split(".")
    time_struct = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    millisecs = int(millisecs_str)
    return time.mktime(time_struct) + float(millisecs) / 1000


class HeadData:
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
        head_data.rotation = eval(csv_record[3])  # yaw, pitch, roll
        return head_data

    @classmethod
    def from_list(cls, head_list):
        head_data = HeadData()
        head_data.userid = head_list[0]
        head_data.pos = head_list[1], head_list[2], head_list[3]
        head_data.rotation = head_list[4], head_list[5], head_list[6]
        head_data.timestamp = head_list[7]
        head_data.pos_prefix_sum = head_list[8], head_list[9], head_list[10]
        return head_data

    @classmethod
    def create_interpolated(cls, data1, data2, cur_time):

        def interpolate(x1, x2, part):
            return x1*part + x2*(1-part)

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


class Touch:
    def __init__(self):
        self.userid = None
        self.pos = avg.Point2D()
        self.timestamp = None


    @classmethod
    def from_list(cls, touch_list):
        touch = Touch()
        touch.userid = touch_list[0]
        touch.pos = avg.Point2D(touch_list[1], touch_list[2])
        touch.timestamp = touch_list[3] - time_offset
        return touch


class User:
    def __init__(self, userid):
        self.userid = userid

        head_data_list = execute_qry("SELECT user, x, y, z, pitch, yaw, roll, time, x_sum, y_sum, z_sum "
                          "FROM head WHERE user = " + str(userid) +
                          " GROUP BY time ORDER BY time;", True)
        self.__head_data = [HeadData.from_list(head_list) for head_list in head_data_list]


        touch_data_list = execute_qry("SELECT user, x, y, time "
                                     "FROM touch WHERE user = " + str(userid) +
                                     " GROUP BY time ORDER BY time;", True)
        self.__touches = [Touch.from_list(touch_list) for touch_list in touch_data_list]

    def get_num_states(self):
        return len(self.__head_data)

    def get_head_position_averaged(self, cur_time, smoothness):

        i = self.__time_to_index(cur_time)
        start_integral = self.__head_data[max(0, i - smoothness/2)].pos_prefix_sum
        end_integral = self.__head_data[min(len(self.__head_data)-1, i + int((smoothness+1)/2))].pos_prefix_sum
        head_position = [(end_integral[0] - start_integral[0]) / smoothness,
                         (end_integral[1] - start_integral[1]) / smoothness,
                         (end_integral[2] - start_integral[2]) / smoothness]
        return head_position

    def get_head_orientation(self, cur_time):
        i = self.__time_to_index(cur_time)
        head_orientation = self.__head_orientations[i]
        return head_orientation

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
        return int(t * len(self.__head_data) / max_time)


def init_globals():
    global max_time
    max_time = (execute_qry("SELECT max(time) FROM head;", True)[0][0] -
            execute_qry("SELECT min(time) FROM head;", True)[0][0])
    global time_offset
    time_offset = execute_qry("SELECT min(time) FROM head;", True)[0][0]

    min_x = execute_qry("SELECT min(x) FROM head;", True)[0][0] - 0.5
    max_x = execute_qry("SELECT max(x) FROM head;", True)[0][0] + 0.5

    min_y = execute_qry("SELECT min(y) FROM head;", True)[0][0]
    max_y = execute_qry("SELECT max(y) FROM head;", True)[0][0]

    global pos_range
    min_z = pos_range[0][2]
    max_z = pos_range[1][2]
    pos_range = ((min_x, min_y, min_z), (max_x, max_y, max_z))
