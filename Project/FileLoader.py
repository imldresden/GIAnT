import colorsys
import csv
import Util
import User
import time
import sys
import database

files = []
data = []
minTime = 0
maxTime = 0
minX = sys.maxint;
minY = sys.maxint;
maxX = -sys.maxint;
maxY = -sys.maxint;



class DataPoint:

    head = 0
    user = -1
    x = 0
    y = 0
    z = 0
    pitch = 0
    yaw = 0
    roll = 0
    timestamp = 0
    tool = 0

    def __init__(self, string):

        global minX, maxX, minY, maxY

        self.head = Util.cleanString(string[0])
        self.user = Util.cleanString(string[1])
        self.x = Util.cleanString(string[2])
        self.y = Util.cleanString(string[3])
        self.z = Util.cleanString(string[4])
        self.pitch = Util.cleanString(string[5])
        self.yaw = Util.cleanString(string[6])
        self.roll = Util.cleanString(string[7])
        self.timestamp = Util.cleanString(string[13])
        self.timestamp = Util.convertTimestamp(self.timestamp)
        self.tool = Util.cleanString(string[12])

        if self.x < minX:
            minX = self.x
        if self.x > maxX:
            maxX = self.x
        if self.y < minY:
            minY = self.y
        if self.y > maxY:
            maxY = self.y

        #self.addToUser()


    def addToUser(self):
        found = False
        user = 0
        for u in User.users:
            if u.id == int(self.user):
                found = True
                user = u
                break
        if not found:
            user = User.User(self.user)

        user.addDataPoint(self)

        if(self.head == "head"):
            user.addHeadDirection((float(self.pitch), float(self.yaw), float(self.roll)))
            user.addLocation((float(self.x)*200, float(self.y)*200, float(self.z)*200))
        else:
            user.addTouch(float(self.x)*200, float(self.y)*200)


def loadAllFiles():
    global maxTime, minTime

    filePaths = loadFile('csv/filelist.txt')
    lastTime = time.time()
    for path in filePaths:
        print("loading")
        completePath = 'csv/'+path[0]
        file = loadCsv(loadFile(completePath))
        print("(" + str(filePaths.index(path)+1) + " / " + str(len(filePaths))+") loaded csv: " + path[0] + "   " + str(len(file)) + " lines in " + str(time.time()-lastTime) + " seconds")
        lastTime = time.time()
        #if filePaths.index(path)>0:
        #    break

    for dataPoint in data:
        dataPoint.timestamp = Util.shiftTimestamp(dataPoint.timestamp)
        if dataPoint.timestamp > maxTime:
            maxTime = dataPoint.timestamp


    usercount = len(User.users)
    for index in range(0, usercount-1):
        hue = index/float(usercount)
        User.users[index].color = colorsys.hsv_to_rgb(hue, 1, 1)

    return



def loadCsv(list):
    global minTime
    file = []
    for line in list:
        split = str(line).split(",")
        if len(file) == 0 or not file[len(file)-1] == split:
            dp = DataPoint(split)
            dp.head = dp.head == 'head'
            # if(minTime>=dp.timestamp):
            #     minTime=dp.timestamp
            #     print "minTime "+str(minTime)
            dp.timestamp -= 56740017
            if(len(file)==0 or file[len(file)-1] != (dp.user, dp.head, dp.x, dp.y, dp.z, dp.pitch, dp.yaw, dp.roll, dp.timestamp)):
                file.append((dp.user, dp.head, dp.x, dp.y, dp.z, dp.pitch, dp.yaw, dp.roll, dp.timestamp))
            # file.append(split)
            # data.append(DataPoint(split))
    #files.append(file)
    database.insertMany(file)
    return file


def loadFile(path):
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        my_list = []
        counter = 0

        for row in reader:
            my_list.append(row)
            #print(counter)

        #my_list = list(reader)
        return my_list



def shiftTimestamps():
    for dataPoint in data:
        dataPoint.timestamp = Util.shiftTimestamp(dataPoint.timestamp)


def getLinesInTimeframe(start, end):
    return data.__getitem__(0)
