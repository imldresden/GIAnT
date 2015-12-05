__author__ = 'KillytheBid'
import sqlite3

USER = 0
HEAD = 1
X_VALUE = 2
Y_VALUE = 3
Z_VALUE = 4
PITCH = 5
YAW = 6
ROLL = 7
TIME = 8


con = None
timestamps = []

normDataPerUser = []

def insert(user, head, x, y, z, pitch, yaw, roll, time):
    executeQry("insert into maintable (user, head, x, y, z, pitch, yaw, roll, time) values ("+
                    str(user) + ", " +
                    str(head) + ", " +
                    str(x) + ", " +
                    str(y) + ", " +
                    str(z) + ", " +
                    str(pitch) + ", " +
                    str(yaw) + ", " +
                    str(roll) + ", " +
                    str(time) + ");")


def createMainTable():
    executeQry("Drop Table if exists maintable")
    executeQry("Create Table maintable ("
                    "id integer primary key autoincrement,"
                    "user tinyint not null,"
                    "head boolean not null,"
                    "x float,"
                    "y float,"
                    "z float,"
                    "pitch float,"
                    "yaw float,"
                    "roll float,"
                    "time int not null"
                    ")")

def createTimeTable():
    executeQry("drop table if exists timetable;")
    executeQry("Create Table timetable (time int, user1 tinyint, user2 tinyint, user3 tinyint, user4 tinyint);")


def createNormalTable():
    executeQry("drop table if exists normaltable;")

    executeQry("Create Table normaltable ("
                    "id integer primary key autoincrement,"
                    "user tinyint not null,"
                    "head boolean not null,"
                    "x float,"
                    "y float,"
                    "z float,"
                    "pitch float,"
                    "yaw float,"
                    "roll float,"
                    "time int not null"
                    ")")

    for userid in range(0,5):
        hundreds = -100
        lastTime = -1
        lastData = 0
        dataList = []

        con = sqlite3.connect("main")
        cur = con.cursor()
        cur.execute("select * from maintable where user="+str(userid)+" and head=1 order by time;")
        while True:
            fetch = cur.fetchmany(501)

            if not fetch:
                break;
            print "fetching 500"
            for row in fetch:
                if lastData == 0:
                    lastData = row
                time = row[9]
                data = list(row)
                data.pop(0)
                oldHundreds = hundreds
                hundreds = int(time/float(100))*100
                if hundreds != oldHundreds:
                    data[8] = hundreds
                    for ind in range(3, 8):
                        try:
                            d2 = hundreds - lastTime
                            d1 = time - hundreds
                            d12 = d1+d2
                            d1 = d1 / float(d12)
                            d2 = d2 / float(d12)
                            data[ind] = d1*lastData[ind] + d2*data[ind]
                        except:
                            continue

                    if hundreds - oldHundreds > 100:
                        for step in range(oldHundreds+100, hundreds, 100):
                            newData = list(data)
                            print "skipped"+str(step)

                            for ind in range(3, 8):
                                try:
                                    d2 = step - lastTime
                                    d1 = time - step
                                    d12 = d1+d2
                                    d1 = d1 / float(d12)
                                    d2 = d2 / float(d12)
                                    newData[ind] = d1*lastData[ind] + d2*data[ind]
                                except:
                                    continue
                            newData[8] = step
                            dataList.append(tuple(newData))

                    dataList.append(tuple(data))
                lastTime = time
                lastData = data

        cur.executemany("insert into normaltable (user, head, x, y, z, pitch, yaw, roll, time) values (?,?,?,?,?,?,?,?,?);", dataList)
        con.commit()
        dataList = []


    con.close()
    # executeQry("drop table if exists userdata")
    # executeQry("create table userdata("
    #                 "id integer primary key autoincrement,"
    #                 "head boolean not null,"
    #                 "x float,"
    #                 "y float,"
    #                 "z float,"
    #                 "pitch float,"
    #                 "yaw float,"
    #                 "roll float,"
    #                 "time int not null"
    #                 ")")
    # executeQry("create table normaltable("
    #            "time primary key not null, "
    #            "u1 int,"
    #            "u2 int,"
    #            "u3 int,"
    #            "u4 int,"
    #            "foreign key(u1) references userdata(id),"
    #            "foreign key(u2) references userdata(id),"
    #            "foreign key(u3) references userdata(id),"
    #            "foreign key(u4) references userdata(id)")



def executeQry(qry, doFetch=False):
    con = sqlite3.connect("main")
    cur = con.cursor()
    cur.execute(qry)
    if(doFetch):
        return cur.fetchall()
    con.commit()
    con.close()


# def many():
#     con = sqlite3.connect("main")
#     cur = con.cursor()
#
#     tim = time.time()
#     list = ""
#     for index in range(0, 500):
#         list = list+" or id = "+str(index)
#     cur.execute("Select * from maintable where id = 1"+list)
#     print cur.fetchall()
#     print 1/(time.time()-tim)
#     con.commit()
#     con.close()


def insertMany(list, useNormalTable=False):
    con = sqlite3.connect("main")

    cur = con.cursor()
    if(useNormalTable):
        cur.executemany("insert into normaltable (user, head, x, y, z, pitch, yaw, roll, time) values (?,?,?,?,?,?,?,?,?);", list)
    else:
        cur.executemany("insert into maintable (user, head, x, y, z, pitch, yaw, roll, time) values (?,?,?,?,?,?,?,?,?);", list)
    con.commit()
    con.close()


def insertAllTimeStamps():
    createTimeTable()
    global timestamps
    con = sqlite3.connect("main")
    cur = con.cursor()
    cur.execute("select distinct time from maintable order by time asc")
    timestamps = cur.fetchall()
    cur.executemany("insert into timetable (time) values (?)", timestamps)
    con.commit()
    con.close()


def loadTimestamps():
    global timestamps
    timestamps = []
    qryresult = executeQry("select * from timetable;", True)
    for r in qryresult:
        timestamps.append((r[0]))


def findTimestamps(start, end, count):
    #start and end are values from 0 to 1
    result = []
    if len(timestamps) == 0:
        loadTimestamps()
    lastTimestamp = timestamps[len(timestamps)-1]
    startTime = int(lastTimestamp * start)
    endTime = int(lastTimestamp * end)
    for i in range(startTime, endTime, (endTime-startTime)/count):
        result.append(getClosestTimestamp(i))
    return result


def getClosestTimestamp(time):
    step = int(len(timestamps)/100 + 1)
    m = 1
    probableSpot = int(time/float(timestamps[len(timestamps)-1]))
    distance = timestamps[probableSpot]-time
    found = False
    while not found:
        if(distance * m >=0):
            while distance * m > 0:
                probableSpot -= step * m
                newDistance = timestamps[min(max(probableSpot,0), len(timestamps)-1)]-time
                if(abs(newDistance)<abs(distance)):
                    distance = newDistance
                else:
                    probableSpot += step * m
                    break

            if step > 1:
                step = int(step * 0.5)

            else:
                found=True
        else:
            m *= -1
    probableSpot = min(max(probableSpot,0), len(timestamps)-1)
    return timestamps[probableSpot]


def fetchNormData():
    global normDataPerUser
    for user in range(1, 5):
        normDataPerUser.append(executeQry("select * from normaltable where user = "+str(user)+" order by time;", True))


#createNormalTable()

#loadTimestamps()
#findTimestamps(0.1, 0.9, 1000)


#many()
#createMainTable()

# lischde = []
#
# for i in range(0, 5000000):
#     lischde.append((1, 1, 1.1,2.2,3.3,5.5,6.6,7.7, 1234567))
#
#
# s=time.time()
# insertMany(lischde)
# print time.time()-s


# createTimeTable()
# s = time.time()
# insertAllTimeStamps()
# print str(time.time()-s) + " to make Timestamps. Count: " + str(len(timestamps))