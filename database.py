import sqlite3, csv
import time
import Util

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

minX = 0
maxX = 0
minTouchX = 0
maxTouchX = 0

minY = 0
maxY = 0
minTouchY = 0
maxTouchY = 0

minZ = 0
maxZ = 0

minTime = 0
maxTime = 0

times = []


# qry: the query to execute (string)
# doFetch: whether data should be fetched and returned
def executeQry(qry, doFetch=False):
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.execute(qry)
    if doFetch:
        return cur.fetchall()
    con.commit()
    con.close()


# table: name of the table (string)
# list: a list of tuples containing the data to insert
def insertMany(list, table):
    con = sqlite3.connect("db")
    cur = con.cursor()
    cur.executemany(
        "INSERT INTO " + str(table) + " (user, head, x, y, z, pitch, yaw, roll, time) VALUES (?,?,?,?,?,?,?,?,?);",
        list)
    con.commit()
    con.close()


# table: name of the table (string)
# columns: columns separated by commas (string) i.e. "id INT, value1 FLOAT, value2 VARCHAR..."
def createTable(table, columns):
    executeQry("DROP TABLE IF EXISTS " + table + ";")
    executeQry("CREATE TABLE " + table + " (" + columns + ");")


# laedt alle Dateien, deren Pfade in der filelist.txt vorhanden sind in die Datenbank
def loadFilesIntoDatabase(filelist):
    filePaths = loadFile('csv/filelist.txt')
    lines = []
    lastTime = time.time()
    for path in filePaths:
        completePath = 'csv/' + path[0]
        print("loading " + str(completePath))
        file = loadCsv(loadFile(completePath))
        print(
            "(" + str(filePaths.index(path) + 1) + " / " + str(len(filePaths)) + ") loaded csv: " + path[
                0] + "   " + str(
                len(file)) + " lines in " + str(time.time() - lastTime) + " seconds")
        lastTime = time.time()

    return


# loads the rows from a csv file and returns a list-hierarchy of it
def loadCsv(rows):
    global minTime
    file = []
    lastline = 0
    for line in rows:
        split = str(line).split(",")
        if lastline == line:
            continue
        else:
            lastline = line
        if len(file) == 0 or not file[len(file) - 1] == split:
            head = Util.cleanString(split[HEAD])

            for i in range(len(split)):
                split[i] = Util.cleanString(split[i])
            lineTuple = (split[USER], head == 'head', split[X_VALUE], split[Y_VALUE], split[Z_VALUE], split[PITCH],
                         split[YAW], split[ROLL], Util.convertTimestamp(split[13]))
            # if len(file)==0 or file[len(file)-1] != lineTuple):
            file.append(lineTuple)

    insertMany(file, "raw")
    return file


# loads the file from the specified path and returns a list of all rows of it
def loadFile(path):
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        my_list = []

        for row in reader:
            my_list.append(row)

        return my_list


# create a table where x, y, z and the time are normalized between 0 and 1
# and equalize the time intervals
def createNormalTable():
    createTable("normaltable", "ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "user TINYINT NOT NULL,"
                               "head BOOLEAN NOT NULL,"
                               "x FLOAT,"
                               "y FLOAT,"
                               "z FLOAT,"
                               "pitch FLOAT,"
                               "yaw FLOAT,"
                               "roll FLOAT,"
                               "time FLOAT NOT NULL")

    # interval in ms (just for calculation, will be normalized between 0 and 1)
    timeStepSize = 50

    # for each user (1-4)
    for userid in range(1, 5):
        lastData = 0
        dataList = []

        con = sqlite3.connect("db")
        cur = con.cursor()

        userStartTime = time.time()

        # two querys, one for head-movement and one for touches
        qrys = []
        qrys.append(
            "SELECT * from raw WHERE user=" + str(userid) + " AND head = 1 AND z != 0 GROUP BY time ORDER BY time;")
        qrys.append(
            "SELECT * from raw WHERE user=" + str(userid) + " AND head = 0 OR z == 0 GROUP BY time ORDER BY time;")

        for qry in qrys:
            print "executing " + qry

            cur.execute(qry)
            fetch = cur.fetchall()

            lastTimeStep = -1

            for row in fetch:

                if (len(dataList) > 500):  # upload 5000 at a time

                    # normalize time before upload
                    for data in dataList:
                        newTime = (data[TIME]) / float(maxTime - minTime)
                        if newTime > 1:
                            print str(data) + " " + str(maxTime) + " " + str(minTime) + " " + str(maxTime - minTime)

                        data[TIME] = newTime

                    # upload
                    cur.executemany(
                        "INSERT INTO normaltable (user, head, x, y, z, pitch, yaw, roll, time) VALUES (?,?,?,?,?,?,?,?,?);",
                        dataList)
                    dataList = []  # clear

                data = list(row)
                data.pop(0)  # remove id

                if qry == qrys[0]:  # if head (has Z-position)
                    data[X_VALUE] = (data[X_VALUE] - minX) / (maxX - minX)
                    data[Y_VALUE] = (data[Y_VALUE] - minY) / (maxY - minY)
                    data[Z_VALUE] = (data[Z_VALUE] - minZ) / (maxZ - minZ)
                else:  # if touch
                    data[X_VALUE] = (data[X_VALUE] - minTouchX) / (maxTouchX - minTouchX)
                    data[Y_VALUE] = (data[Y_VALUE] - minTouchY) / (maxTouchY - minTouchY)

                data[TIME] -= minTime  # shift time to start at 0

                # time "rounded" to closest divisible of timeStepSize
                timeStep = int(data[TIME] / timeStepSize) * timeStepSize

                # initialize first value
                if lastData == 0:
                    lastData = list(data)
                    data[TIME] = timeStep
                    dataList.append(data)
                    continue

                if timeStep > lastTimeStep:  # if a new step is reached

                    newData = list(data)

                    # if at least 1 step would be skipped. calculate the steps between
                    if data[HEAD] == 1 & lastTimeStep + timeStepSize < timeStep:
                        lastTime = lastData[TIME]
                        newestTime = data[TIME]
                        # for each skipped step
                        for interpolatedTime in range(lastTimeStep, data[TIME], timeStepSize):
                            # progress/percentage of the step between the last time and the new time
                            percentage = min(1, max(0, (interpolatedTime - lastTime) / float(newestTime - lastTime)))

                            # calculate x and y values
                            newData[X_VALUE] = percentage * float(data[X_VALUE]) + (1 - percentage) * float(
                                lastData[X_VALUE])
                            newData[Y_VALUE] = percentage * float(data[Y_VALUE]) + (1 - percentage) * float(
                                lastData[Y_VALUE])

                            # if this is not a touch
                            if qry == qrys[0]:
                                newData[HEAD] = 1
                                newData[Z_VALUE] = percentage * float(data[Z_VALUE]) + (1 - percentage) * float(
                                    lastData[Z_VALUE])
                            else:
                                newData[HEAD] = 0
                            newData[TIME] = interpolatedTime  # set time to step
                            dataList.append(list(newData))  # prepare for upload
                            lastTimeStep = timeStep
                    else:
                        lastTime = lastData[TIME]
                        newestTime = data[TIME]
                        # progress/percentage of the step between the last time and the new time
                        percentage = min(1, max(0, (timeStep - lastTime) / float(newestTime - lastTime)))

                        # calculate x and y values
                        newData[X_VALUE] = percentage * float(data[X_VALUE]) + (1 - percentage) * float(
                            lastData[X_VALUE])
                        newData[Y_VALUE] = percentage * float(data[Y_VALUE]) + (1 - percentage) * float(
                            lastData[Y_VALUE])

                        # if this is not a touch
                        if qry == qrys[0]:
                            newData[HEAD] = 1
                            newData[Z_VALUE] = percentage * float(data[Z_VALUE]) + (1 - percentage) * float(
                                lastData[Z_VALUE])
                        else:
                            newData[HEAD] = 0
                        newData[TIME] = timeStep  # set time to step
                        dataList.append(newData)  # prepare for upload
                        lastTimeStep = timeStep

                lastData = data

        # normalize time before upload
        for data in dataList:
            newTime = (data[TIME]) / float(maxTime - minTime)
            data[TIME] = newTime
            if newTime > 1:
                print data

        # upload
        cur.executemany(
            "INSERT INTO normaltable (user, head, x, y, z, pitch, yaw, roll, time) VALUES (?,?,?,?,?,?,?,?,?);",
            dataList)

        con.commit()

        print "done in " + str(time.time() - userStartTime)

    con.close()


def initValues():
    global minX, maxX, minTouchX, maxTouchX, minY, maxY, minTouchY, maxTouchY, minZ, maxZ, minTime, maxTime, times
    minX = executeQry("SELECT min(x) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]
    maxX = executeQry("SELECT max(x) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]

    minY = executeQry("SELECT min(y) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]
    maxY = executeQry("SELECT max(y) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]

    minZ = executeQry("SELECT min(z) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]
    maxZ = executeQry("SELECT max(z) FROM raw WHERE z != '' OR HEAD = 1;", True)[0][0]

    minTouchX = executeQry("SELECT min(x) FROM raw WHERE z = '' OR HEAD = 0;", True)[0][0]
    maxTouchX = executeQry("SELECT max(x) FROM raw WHERE z = '' OR HEAD = 0;", True)[0][0]

    minTouchY = executeQry("SELECT min(y) FROM raw WHERE z = '' OR HEAD = 0;", True)[0][0]
    maxTouchY = executeQry("SELECT max(y) FROM raw WHERE z = '' OR HEAD = 0;", True)[0][0]

    minTime = executeQry("SELECT min(time) FROM raw;", True)[0][0]
    maxTime = executeQry("SELECT max(time) FROM raw;", True)[0][0]

    times = executeQry("SELECT time FROM normaltable GROUP BY time ORDER BY time;", True)


def setupRawTable():
    rawColumns = "id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                 "user TINYINT NOT NULL, " \
                 "head BOOLEAN NOT NULL, " \
                 "x FLOAT, " \
                 "y FLOAT, " \
                 "z FLOAT, " \
                 "pitch FLOAT, " \
                 "yaw FLOAT, " \
                 "roll FLOAT, " \
                 "time INT"

    createTable("raw", rawColumns)
    loadFilesIntoDatabase("csv/filelist.txt")


def setupDatabase():
    setupRawTable()
    createNormalTable()


initValues()
# setupDatabase()
