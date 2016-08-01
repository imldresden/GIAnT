#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sqlite3
import pat_model

TIME_STEP = 1./30            # User position data stored with 30 FPS


def create_table(table, columns):
    """
    :param table: name of the table (string)
    :param columns: columns separated by commas (string) i.e. "id INT, value1 FLOAT, value2 VARCHAR..."
    :return:
    """
    pat_model.execute_qry("DROP TABLE IF EXISTS " + table + ";")
    pat_model.execute_qry("CREATE TABLE " + table + " (" + columns + ");")


def import_optitrack(session):
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

    with open(session.data_dir+"/"+session.optitrack_filename) as f:
        reader = csv.reader(f)
        csv_data = list(reader)
        csv_data.pop(0)
    last_lines = [None] * session.number_of_users
    last_db_time = [None] * session.number_of_users
    last_interpol_data = [None] * session.number_of_users
    db_list = []
    for data_line in csv_data:
        head_data = pat_model.HeadData.from_csv(data_line, session.date)
        userid = head_data.userid
        last_data = last_lines[userid]
        if (last_data is not None) and (last_data.timestamp == head_data.timestamp):  # Discard equal lines
            continue
        while last_db_time[userid] < head_data.timestamp:
            # The original (csv) data has irregular timestamps, the db should contain data every
            # TIME_STEP.
            interpol_data = pat_model.HeadData.create_interpolated(last_data, head_data, last_db_time[userid])
            interpol_data.calc_sums(last_interpol_data[head_data.userid])
            db_list.append(interpol_data.as_list())
            if last_db_time[userid] is None:
                last_db_time[userid] = head_data.timestamp
            else:
                last_db_time[userid] += TIME_STEP
            last_interpol_data[userid] = interpol_data
        last_lines[userid] = head_data
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

    create_table("touch", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                         "user TINYINT NOT NULL,"
                         "x FLOAT,"
                         "y FLOAT,"
                         "time FLOAT NOT NULL,"
                         "duration FLOAT NOT NULL")

    with open(session.data_dir + "/" + session.touch_filename) as f:
        reader = csv.reader(f)
        csv_data = list(reader)
        csv_data.pop(0)
    db_list = []
    last_time = 0
    for data in csv_data:
        timestamp = pat_model.csvtime_to_float(session.date, data[0])
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

    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.executemany("INSERT INTO touch (user, x, y, time, duration) VALUES (?,?,?,?,?);", db_list)
    con.commit()
    con.close()

def setup():
    session = pat_model.create_session()
    import_optitrack(session)
    import_touches(session)

setup()
print "Database setup complete."
