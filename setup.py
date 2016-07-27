#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import sqlite3
import pat_model

DATA_DIR = "Study Data/Session 3"
OPTITRACK_FILENAME = "optitrack_Beginner's Village15-24_17-03-2016_log.csv"
TOUCH_FILENAME = "touch_Beginner's Village15-24_17-03-2016_log.csv"
DATE = "2016-03-17"


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
    last_line = None
    db_list = []
    for data_line in csv_data:
        head_data = pat_model.HeadData.from_csv(data_line, DATE, last_line)
        if (last_line is None) or (head_data != last_line):  # Discard equal lines
            last_line = head_data
            db_list.append(head_data.as_list())
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO head (user, x, y, z, pitch, yaw, roll, time, x_sum, y_sum, z_sum) VALUES (?,?,?,?,?,?,?,?,?,?,?);", db_list)
    con.commit()
    con.close()


import_optitrack()

print "Database setup complete."
