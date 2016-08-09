#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sqlite3
import pat_model
import time

from libavg import player

TIME_STEP = 1./30            # User position data stored with 30 FPS

player.loadPlugin("plots")


# Converts time from csv format to float seconds since 1970.
def csvtime_to_float(date, csv_time):
    time_str = date + " " + csv_time
    (time_str, millisecs_str) = time_str.split(".")
    time_struct = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    millisecs = int(millisecs_str)
    return time.mktime(time_struct) + float(millisecs) / 1000


def create_table(table, columns):
    """
    :param table: name of the table (string)
    :param columns: columns separated by commas (string) i.e. "id INT, value1 FLOAT, value2 VARCHAR..."
    :return:
    """
    pat_model.execute_qry("DROP TABLE IF EXISTS " + table + ";")
    pat_model.execute_qry("CREATE TABLE " + table + " (" + columns + ");")


def import_optitrack(session):

    def head_data_from_csv(csv_record, date):
        timestamp = csvtime_to_float(date, csv_record[0])
        userid = eval(csv_record[1])-1
        pos = list(eval(csv_record[2]))
        # pos is in Meters, origin is lower left corner of the wall.
        # In the CSV file:
        #   If facing the wall, x points left, y up, z into the wall
        # In the DB:
        #   If facing the wall, x points right, y up, z away from the wall
        pos[0] = -pos[0]
        pos[2] = -pos[2]
        # Rotation is yaw, pitch, roll, origin is facing wall.
        rotation = eval(csv_record[3])
        head_data = plots.HeadData(userid, pos, rotation, timestamp)
        return head_data

    def create_interpolated_head_data(data1, data2, cur_time, prev_data):

        def interpolate(x1, x2, ratio):
            return x1 * ratio + x2 * (1 - ratio)

        if data1 is None:
            data = data2
        else:
            part = (cur_time - data1.time) / (data2.time - data1.time)
            assert(data1.userid == data2.userid)
            pos = [interpolate(data1.pos[0], data2.pos[0], part),
                    interpolate(data1.pos[1], data2.pos[1], part),
                    interpolate(data1.pos[2], data2.pos[2], part)]
            rot = [interpolate(data1.rot[0], data2.rot[0], part),
                    interpolate(data1.rot[1], data2.rot[1], part),
                    interpolate(data1.rot[2], data2.rot[2], part)]
            data = plots.HeadData(data1.userid, pos, rot, cur_time)
        if prev_data:
            prev_prefix_sum = prev_data.posPrefixSum
            data.posPrefixSum = (
                prev_prefix_sum[0] + data.pos[0],
                prev_prefix_sum[1] + data.pos[1],
                prev_prefix_sum[2] + data.pos[2])
        else:
            data.posPrefixSum = data.pos
        return data

    def head_data_to_list(head):
        return (head.userid,
                head.pos[0], head.pos[1], head.pos[2],
                head.rot[0], head.rot[1], head.rot[2],
                head.time,
                head.posPrefixSum[0], head.posPrefixSum[1], head.posPrefixSum[2])

    create_table("head", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                         "user TINYINT NOT NULL,"
                         "x FLOAT,"
                         "y FLOAT,"
                         "z FLOAT,"
                         "pitch FLOAT,"
                         "yaw FLOAT,"
                         "roll FLOAT,"
                         "time FLOAT NOT NULL,"
                         "x_sum FLOAT,"          # prefix sum for quick calculation of average positions.
                         "y_sum FLOAT,"
                         "z_sum FLOAT")

    print "Importing optitrack data:"
    print "  Reading csv"
    with open(session.data_dir+"/"+session.optitrack_filename) as f:
        reader = csv.reader(f)
        csv_data = list(reader)
        csv_data.pop(0)
    print "  Processing"
    last_lines = [None] * session.num_users
    last_db_time = [None] * session.num_users
    last_interpol_data = [None] * session.num_users
    db_list = []
    for data_line in csv_data:
        head_data = head_data_from_csv(data_line, session.date)
        userid = head_data.userid
        last_data = last_lines[userid]
        if (last_data is not None) and (last_data.time == head_data.time):  # Discard equal lines
            continue
        while last_db_time[userid] < head_data.time:
            # The original (csv) data has irregular timestamps, the db should contain data every
            # TIME_STEP.
            interpol_data = create_interpolated_head_data(last_data, head_data, last_db_time[userid],
                    last_interpol_data[head_data.userid])
            db_list.append(head_data_to_list(interpol_data))
            if last_db_time[userid] is None:
                last_db_time[userid] = head_data.time
            else:
                last_db_time[userid] += TIME_STEP
            last_interpol_data[userid] = interpol_data
        last_lines[userid] = head_data
    print "  Writing database"
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO head (user, x, y, z, pitch, yaw, roll, time, x_sum, y_sum, z_sum) VALUES (?,?,?,?,?,?,?,?,?,?,?);", db_list)
    con.commit()
    con.close()


def import_touches(session):
    def tool_to_userid(tool):
        if tool == "Pick":
            return 0
        elif tool == "Girder":
            return 1
        elif tool == "Lantern":
            return 2
        elif tool == "Ladder":
            return 3

    print "Importing touch data:"
    create_table("touch", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                         "user TINYINT NOT NULL,"
                         "x FLOAT,"
                         "y FLOAT,"
                         "time FLOAT NOT NULL,"
                         "duration FLOAT NOT NULL")


    print "  Reading csv"
    with open(session.data_dir + "/" + session.touch_filename) as f:
        reader = csv.reader(f)
        csv_data = list(reader)
        csv_data.pop(0)
    print "  Processing"
    db_list = []
    last_time = 0
    for data in csv_data:
        timestamp = csvtime_to_float(session.date, data[0])
        pos = list(eval(data[1]))
        userid = tool_to_userid(data[2])
        if userid is None:
            continue
        touch = [userid, pos[0], pos[1], timestamp, 0.03]
        if touch[3] > last_time + 0.1:
            # New touch
            db_list.append(touch)  # prepare for upload
        else:
            # Touch continuation
            touch[4] += touch[3] - last_time
            db_list[-1] = touch
        last_time = touch[3]

    print "  Writing database"
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.executemany("INSERT INTO touch (user, x, y, time, duration) VALUES (?,?,?,?,?);", db_list)
    con.commit()
    con.close()

def setup():
    session = pat_model.create_session()
    print "---- "+session.optitrack_filename+" ----"
    import_optitrack(session)
    import_touches(session)

setup()
print "Database setup complete."
