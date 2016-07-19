# -*- coding: utf-8 -*-

import sqlite3
import csv
import time
import util
import sys

# Positions in the database
HEAD = 0
USER = 1
X_VALUE = 2
Y_VALUE = 3
Z_VALUE = 4
PITCH = 5
YAW = 6
ROLL = 7
TIME = 8

min_x = 0
max_x = 0
min_touch_x = 0
max_touch_x = 0

min_y = 0
max_y = 0
min_touch_y = 0
max_touch_y = 0

min_z = 0
max_z = 0

min_time = 0
max_time = 0

times = []
timestampOffset = sys.maxint


def executeQry(qry, doFetch=False):
    """
    :param qry: the query to execute (string)
    :param doFetch:  whether data should be fetched and returned
    :return:
    """
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.execute(qry)
    if doFetch:
        return cur.fetchall()
    con.commit()
    con.close()


def insert_many(list, table, value_names):
    """
    :param list: a list of tuples containing the data to insert
    :param table: name of the table (string)
    :param value_names:
    :return:
    """
    con = sqlite3.connect("db")
    cur = con.cursor()
    qry = "INSERT INTO " + str(table) + " ("
    for name in value_names:
        qry = qry + str(name) + ", "
    qry = qry[:-2]
    qry = qry + ") VALUES ("
    for name in value_names:
        qry = qry + "?,"
    qry = qry[:-1] + ");"
    cur.executemany(qry, list)
    con.commit()
    con.close()


def create_table(table, columns):
    """
    :param table: name of the table (string)
    :param columns: columns separated by commas (string) i.e. "id INT, value1 FLOAT, value2 VARCHAR..."
    :return:
    """
    executeQry("DROP TABLE IF EXISTS " + table + ";")
    executeQry("CREATE TABLE " + table + " (" + columns + ");")


def load_files_into_database(filelist):
    """
    Loads files listed in filelist.txt in database
    :param filelist:
    :return:
    """
    file_paths = load_file('csv/filelist.txt')
    last_time = time.time()
    for path in file_paths:
        if not path[0].endswith(".csv"):
            continue

        completePath = 'csv/' + path[0]
        print("loading " + str(completePath))
        file = load_csv(load_file(completePath))
        print("(" + str(file_paths.index(path) + 1) + " / " + str(len(file_paths)) + ") loaded csv: " +
              path[0] + "   " + str(len(file)) + " lines in " + str(time.time() - last_time) + " seconds")
        last_time = time.time()

    return


def load_csv(rows):
    """
    Loads the rows from a csv file and returns a list-hierarchy of it
    :param rows:
    :return: list hierarchy of file
    """
    import util
    global min_time
    file = []
    lastline = 0
    for line in rows:
        split = str(line).split(",")
        if lastline == line:
            continue
        else:
            lastline = line
        if len(file) == 0 or not file[len(file) - 1] == split:
            head = cleanString(split[HEAD])

            for i in range(len(split)):
                split[i] = cleanString(split[i])
            lineTuple = (split[USER], head == 'head', split[X_VALUE], split[Y_VALUE], split[Z_VALUE], split[PITCH],
                         split[YAW], split[ROLL], convertTimestamp(split[13]))
            file.append(lineTuple)

    insert_many(file, "raw", ["user", "head", "x", "y", "z", "pitch", "yaw", "roll", "time"])
    return file


def load_file(path):
    """
    Loads the file from the specified path and returns a list of all rows of it.
    :param path: path to file
    :return: list of all rows of file
    """
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        my_list = []

        for row in reader:
            my_list.append(row)

        return my_list


def create_head_table():
    create_table("headtable", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                              "user TINYINT NOT NULL,"
                              "x FLOAT,"
                              "y FLOAT,"
                              "z FLOAT,"
                              "pitch FLOAT,"
                              "yaw FLOAT,"
                              "roll FLOAT,"
                              "time FLOAT NOT NULL")

    # for each user (1-4)
    for userid in range(1, 5):
        import global_values
        last_data = 0
        datalist = []

        con = sqlite3.connect("db")
        cur = con.cursor()

        user_start_time = time.time()

        # two querys, one for head-movement and one for touches
        qry = "SELECT user, x, y, z, pitch, yaw, roll, time from raw WHERE user=" + str(userid) +\
              " AND head = 1 AND z != 0 GROUP BY time ORDER BY time;"
        COL_X = 1
        COL_Y = 2
        COL_Z = 3
        COL_TIME = 7
        print "executing " + qry

        cur.execute(qry)
        fetch = cur.fetchall()

        last_time_step = -1

        for row in fetch:
            # upload 5000 at a time
            if len(datalist) > 5000:
                # upload
                cur.executemany(
                    "INSERT INTO headtable (user, x, y, z, pitch, yaw, roll, time) VALUES (?,?,?,?,?,?,?,?);", datalist)
                datalist = []  # clear
                con.commit()

            new_data = list(row)

            new_data[COL_X] *= 100
            new_data[COL_Y] *= 100
            new_data[COL_Z] *= 100

            new_data[COL_TIME] -= min_time  # shift time to start at 0

            # time "rounded" to closest divisible of time_stepSize
            time_step = int(new_data[COL_TIME] / global_values.time_step_size) * global_values.time_step_size

            # initialize first values
            if last_data == 0:
                last_data = list(new_data)
                new_data[COL_TIME] = time_step
                datalist.append(new_data)
                continue

            # if a new step is reached
            if time_step > last_time_step:

                new_data = list(new_data)

                # if at least 1 step would be skipped. calculate the steps between
                if last_time_step + global_values.time_step_size < time_step:
                    last_time = last_data[COL_TIME]
                    newest_time = new_data[COL_TIME]
                    # for each skipped step
                    interpolated_list = []
                    for interpolated_time in range(last_time_step, int(new_data[COL_TIME]),
                                                   global_values.time_step_size):
                        # progress/percentage of the step between the last time and the new time
                        percentage = min(1, max(0, (interpolated_time - last_time) / float(newest_time - last_time)))

                        # calculate x and y values
                        new_data[COL_X] = percentage * float(new_data[COL_X]) + (1 - percentage) * float(last_data[COL_X])
                        new_data[COL_Y] = percentage * float(new_data[COL_Y]) + (1 - percentage) * float(last_data[COL_Y])
                        new_data[COL_Z] = percentage * float(new_data[COL_Z]) + (1 - percentage) * float(last_data[COL_Z])
                        new_data[COL_TIME] = interpolated_time  # set time to step
                        interpolated_list.append(list(new_data))
                        last_time_step = time_step

                    for new_data in interpolated_list:
                        datalist.append(new_data)  # prepare for upload

                else:
                    last_time = last_data[COL_TIME]
                    newest_time = new_data[COL_TIME]
                    # progress/percentage of the step between the last time and the new time
                    percentage = min(1, max(0, (time_step - last_time) / float(newest_time - last_time)))

                    # calculate x and y values
                    new_data[COL_X] = percentage * float(new_data[COL_X]) + (1 - percentage) * float(last_data[COL_X])
                    new_data[COL_Y] = percentage * float(new_data[COL_Y]) + (1 - percentage) * float(last_data[COL_Y])
                    new_data[COL_Z] = percentage * float(new_data[COL_Z]) + (1 - percentage) * float(last_data[COL_Z])

                    new_data[COL_TIME] = time_step  # set time to step
                    datalist.append(new_data)  # prepare for upload
                    last_time_step = time_step

            last_data = new_data

        # upload
        if len(datalist) > 0:
            query = "INSERT INTO headtable (user, x, y, z, pitch, yaw, roll, time) VALUES (?,?,?,?,?,?,?,?);"
            print "  " + query + "  first Element: " + str(datalist[0])
            cur.executemany(query, datalist)
        con.commit()

    print "done in " + str(time.time() - user_start_time)

    con.close()


def create_head_table_integral():
    create_table("headtableintegral", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                                      "user TINYINT NOT NULL,"
                                      "x FLOAT,"
                                      "y FLOAT,"
                                      "z FLOAT,"
                                      "pitch FLOAT,"
                                      "yaw FLOAT,"
                                      "roll FLOAT,"
                                      "time FLOAT NOT NULL")
    for userid in range(1, 5):
        user_head_data = executeQry("SELECT user, x, y, z, pitch, yaw, roll, time FROM headtable WHERE user = " +
                                    str(userid) + " GROUP BY time ORDER BY time;", True)
        for i in range(0, len(user_head_data)):
            for column in range(1, 4):
                as_list = list(user_head_data[i])
                as_list[column] += user_head_data[i - 1][column]
                user_head_data[i] = tuple(as_list)

        insert_many(user_head_data, "headtableintegral", ["user", "x", "y", "z", "pitch", "yaw", "roll", "time"])


def create_viewpoint_table():
    create_table("viewpointtable", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                                   "user TINYINT NOT NULL,"
                                   "x FLOAT,"
                                   "y FLOAT,"
                                   "time FLOAT NOT NULL")
    for userid in range(1, 5):
        user_head_data = executeQry("SELECT x, y, z, pitch, yaw, time FROM headtable WHERE user = " +
                                    str(userid) + " GROUP BY time ORDER BY time;", True)
        user_view_point_data = []
        for i in range(0, len(user_head_data)):
            data = user_head_data[i]
            pitch = data[3]
            yaw = data[4]
            x = data[0]
            y = data[1]
            z = data[2]
            time = data[5]
            view_vector = util.get_look_direction(pitch, yaw)
            multiplier = z / view_vector[2]
            view_point = (x - view_vector[0] * multiplier, y - view_vector[1] * multiplier)
            user_view_point_data.append([userid, view_point[0], view_point[1], time])

        insert_many(user_view_point_data, "viewpointtable", ["user", "x", "y", "time"])


def create_viewpoint_table_integral():
    create_table("viewpointintegral", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                                      "user TINYINT NOT NULL,"
                                      "x FLOAT,"
                                      "y FLOAT,"
                                      "time FLOAT NOT NULL")
    for userid in range(1, 5):
        user_viewpoints = executeQry("SELECT user, x, y, time FROM headtable WHERE user = " + str(userid) +
                                     " GROUP BY time ORDER BY time;", True)
        for i in range(0, len(user_viewpoints)):
            for column in range(1, 3):
                as_list = list(user_viewpoints[i])
                as_list[column] += user_viewpoints[i - 1][column]
                user_viewpoints[i] = tuple(as_list)

        insert_many(user_viewpoints, "viewpointintegral", ["user", "x", "y", "time"])


def create_touch_table(wall_screen_resolution):
    create_table("touchtable", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "user TINYINT NOT NULL,"
                               "x FLOAT,"
                               "y FLOAT,"
                               "time FLOAT NOT NULL")

    # for each user (1-4)
    for userid in range(1, 5):
        import global_values
        datalist = []

        con = sqlite3.connect("db")
        cur = con.cursor()

        user_start_time = time.time()

        # two querys, one for head-movement and one for touches
        qry = "SELECT user, x, y, time from raw WHERE user=" + str(userid) + \
              " AND head = 0 GROUP BY time ORDER BY time;"

        COL_X = 1
        COL_Y = 2
        COL_TIME = 3

        print "executing " + qry
        cur.execute(qry)
        fetch = cur.fetchall()

        print "uploading " + str(len(fetch))
        for row in fetch:

            if len(datalist) >= 500:  # upload 500 at a time
                # upload
                cur.executemany("INSERT INTO touchtable (user, x, y, time) VALUES (?,?,?,?);", datalist)
                con.commit()
                datalist = []  # clear

            data = list(row)

            data[COL_X] = data[COL_X] * global_values.wall_width / wall_screen_resolution[0]

            data[COL_Y] = 40 + (wall_screen_resolution[1] - data[COL_Y]) * global_values.wall_height / wall_screen_resolution[1]

            data[COL_TIME] -= min_time  # shift time to start at 0

            new_data = list(data)
            datalist.append(new_data)  # prepare for upload

        if len(datalist) > 0:
            # upload
            cur.executemany("INSERT INTO touchtable (user, x, y, time) VALUES (?,?,?,?);", datalist)
            con.commit()
            datalist = []

    con.close()


def setup_raw_table():
    raw_olumns = "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                 "user TINYINT NOT NULL, " \
                 "head BOOLEAN NOT NULL, " \
                 "x FLOAT, " \
                 "y FLOAT, " \
                 "z FLOAT, " \
                 "pitch FLOAT, " \
                 "yaw FLOAT, " \
                 "roll FLOAT, " \
                 "time INT"

    create_table("raw", raw_olumns)
    load_files_into_database("csv/filelist.txt")


def init_raw_values():
    global min_x, max_x, min_touch_x, max_touch_x, min_y, max_y, min_touch_y, max_touch_y, min_z, max_z
    global min_time, max_time, times
    min_x = executeQry("SELECT min(x) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]
    max_x = executeQry("SELECT max(x) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]

    min_y = executeQry("SELECT min(y) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]
    max_y = executeQry("SELECT max(y) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]

    min_z = executeQry("SELECT min(z) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]
    max_z = executeQry("SELECT max(z) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]

    min_touch_x = executeQry("SELECT min(x) FROM raw WHERE z = '' OR HEAD = 0;", True)[0][0]
    max_touch_x = executeQry("SELECT max(x) FROM raw WHERE z = '' OR HEAD = 0;", True)[0][0]

    min_touch_y = executeQry("SELECT min(y) FROM raw WHERE z = '' OR HEAD = 0;", True)[0][0]
    max_touch_y = executeQry("SELECT max(y) FROM raw WHERE z = '' OR HEAD = 0;", True)[0][0]

    min_time = executeQry("SELECT min(time) FROM raw;", True)[0][0]
    max_time = executeQry("SELECT max(time) FROM raw;", True)[0][0]


def init_values():
    global min_x, max_x, min_touch_x, max_touch_x, min_y, max_y, min_touch_y, max_touch_y, min_z, max_z
    global min_time, max_time, times
    try:
        min_x = executeQry("SELECT min(x) FROM headtable;", True)[0][0]
        max_x = executeQry("SELECT max(x) FROM headtable;", True)[0][0]

        min_y = executeQry("SELECT min(y) FROM headtable;", True)[0][0]
        max_y = executeQry("SELECT max(y) FROM headtable;", True)[0][0]

        min_z = executeQry("SELECT min(z) FROM headtable;", True)[0][0]
        max_z = executeQry("SELECT max(z) FROM headtable;", True)[0][0]

        min_touch_x = executeQry("SELECT min(x) FROM touchtable;", True)[0][0]
        max_touch_x = executeQry("SELECT max(x) FROM touchtable;", True)[0][0]

        min_touch_y = executeQry("SELECT min(y) FROM touchtable;", True)[0][0]
        max_touch_y = executeQry("SELECT max(y) FROM touchtable;", True)[0][0]

        min_time = executeQry("SELECT min(time) FROM headtable;", True)[0][0]
        max_time = executeQry("SELECT max(time) FROM headtable;", True)[0][0]
    except:
        print "Database not set up"


def get_head_positions(userid):
    return executeQry("SELECT x, y, z, time FROM headtable WHERE user = " + str(userid) +
                      " GROUP BY time ORDER BY time;", True)


def get_head_positions_integral(userid):
    return executeQry("SELECT x, y, z, time FROM headtableintegral WHERE user = " + str(userid) +
                      " GROUP BY time ORDER BY time;", True)


def get_head_positions_optimized(userid):
    return executeQry("SELECT x, y, z, time FROM headtableoptimized WHERE user = " + str(userid) +
                      " ORDER BY time;", True)


def get_head_orientations(userid):
    return executeQry("SELECT pitch, yaw, roll, time FROM headtableintegral WHERE user = " + str(userid) +
                      " GROUP BY time ORDER BY time;", True)


def get_touch_positions(userid):
    return executeQry("SELECT x, y, time FROM touchtable WHERE user = " + str(userid) + ";", True)


def get_view_points(userid):
    return executeQry("SELECT x, y, time FROM viewpointtable WHERE user = " + str(userid) +
                      " GROUP BY time ORDER BY time;", True)


def get_view_points_integral(userid):
    return executeQry("SELECT x, y, time FROM viewpointintegral WHERE user = " + str(userid) + " ORDER BY time;", True)


def convertTimestamp(timestamp):
    """
    Turns the Timestring into a Number of milliseconds.
    :param timestamp:
    :return:
    """
    global timestampOffset
    split = timestamp.split(":")
    split[2] = float(str(split[2])) * 1000  # converting into whole milliseconds
    hours = int(split[0]) * 60 * 60 * 1000
    minutes = int(split[1]) * 60 * 1000
    milliseconds = int(split[2])
    result = hours + minutes + milliseconds
    if result < timestampOffset:
        timestampOffset = result
    return result


def cleanString(string):
    patterns = ("\\", "\'", "[", " ", "]")
    result = string
    for pattern in patterns:
        result = result.replace(pattern, "")
    return result


def setup_database(wall_screen_resolution):
    print "loading csv files into database:"
    setup_raw_table()
    print "tables created 1/7"
    init_raw_values()
    print "tables created 2/7"
    create_head_table()
    print "tables created 3/7"
    create_head_table_integral()
    print "tables created 4/7"
    create_viewpoint_table()
    print "tables created 5/7"
    create_viewpoint_table_integral()
    print "tables created 6/7"
    create_touch_table(wall_screen_resolution)
    print "tables created 7/7"


init_values()
