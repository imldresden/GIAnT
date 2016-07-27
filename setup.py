#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv, time
import sqlite3

DATA_DIR = "Study Data/Session 3"
OPTITRACK_FILENAME = "optitrack_Beginner's Village15-24_17-03-2016_log.csv"
TOUCH_FILENAME = "touch_Beginner's Village15-24_17-03-2016_log.csv"
DATE = "2016-03-17"


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


def create_table(table, columns):
    """
    :param table: name of the table (string)
    :param columns: columns separated by commas (string) i.e. "id INT, value1 FLOAT, value2 VARCHAR..."
    :return:
    """
    execute_qry("DROP TABLE IF EXISTS " + table + ";")
    execute_qry("CREATE TABLE " + table + " (" + columns + ");")


# Converts time from csv format to float seconds since 1970.
def csvtime_to_float(csv_time):
    time_str = DATE + " " + csv_time
    (time_str, millisecs_str) = time_str.split(".")
    time_struct = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    millisecs = int(millisecs_str)
    return time.mktime(time_struct) + float(millisecs) / 1000


class HeadData:
    def __init__(self, csv_record):
        self.timestamp = csvtime_to_float(csv_record[0])
        self.userid = eval(csv_record[1])
        self.pos = eval(csv_record[2])
        self.rotation = eval(csv_record[3])

    def as_list(self):
        return (self.userid,
                self.pos[0], self.pos[1], self.pos[2],
                self.rotation[0], self.rotation[1], self.rotation[2],
                self.timestamp)

    def __eq__(self, other):
        return self.timestamp == other.timestamp and self.userid == other.userid

    def __ne__(self, other):
        return not(self == other)


def import_optitrack():
    create_table("head", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "user TINYINT NOT NULL,"
                              "x FLOAT,"
                              "y FLOAT,"
                              "z FLOAT,"
                              "pitch FLOAT,"
                              "yaw FLOAT,"
                              "roll FLOAT,"
                              "time FLOAT NOT NULL")

    with open(DATA_DIR+"/"+OPTITRACK_FILENAME) as f:
        reader = csv.reader(f)
        csv_data = list(reader)
        csv_data.pop(0)
    last_line = None
    db_list = []
    for data_line in csv_data:
        head_data = HeadData(data_line)
        if (last_line is None) or (head_data != last_line): # Discard equal lines
            last_line = head_data
            db_list.append(head_data.as_list())
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO head (user, x, y, z, pitch, yaw, roll, time) VALUES (?,?,?,?,?,?,?,?);", db_list)
    con.commit()
    con.close()


import_optitrack()

print "Database setup complete."
