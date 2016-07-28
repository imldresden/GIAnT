#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sqlite3
import pat_model

DATA_DIR = "Study Data/Session 3"
OPTITRACK_FILENAME = "optitrack_Beginner's Village15-24_17-03-2016_log.csv"
TOUCH_FILENAME = "touch_Beginner's Village15-24_17-03-2016_log.csv"
DATE = "2016-03-17"
NUMBER_OF_USERS = 4
TIME_STEP = 1./30            # User position data stored with 30 FPS


def create_table(table, columns):
    """
    :param table: name of the table (string)
    :param columns: columns separated by commas (string) i.e. "id INT, value1 FLOAT, value2 VARCHAR..."
    :return:
    """
    pat_model.execute_qry("DROP TABLE IF EXISTS " + table + ";")
    pat_model.execute_qry("CREATE TABLE " + table + " (" + columns + ");")


def import_optitrack():
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

    with open(DATA_DIR+"/"+OPTITRACK_FILENAME) as f:
        reader = csv.reader(f)
        csv_data = list(reader)
        csv_data.pop(0)
    last_lines = [None] * NUMBER_OF_USERS
    last_db_time = [None] * NUMBER_OF_USERS
    last_interpol_data = [None] * NUMBER_OF_USERS
    db_list = []
    i = 0
    for data_line in csv_data:
        head_data = pat_model.HeadData.from_csv(data_line, DATE)
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


import_optitrack()

print "Database setup complete."
