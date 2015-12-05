import Draw
import User
import database
from libavg import app


class VerticalLines:
    users = []
    lineThickness = 10
    userlines = []

    lastZoom = 1
    lastOffset = 0

    def __init__(self):
        self.users = User.users

    def drawFrame(self, parent, zoom, offset): #start, end for the timeframe of the visualization
        if self.lastOffset != offset or len(self.userlines)==0 or self.lastZoom != zoom:
            self.userlines = []
            self.lastZoom = zoom
            self.lastOffset = offset
            resolution = Draw.MainDrawer.resolution

            for userID in range(1,5):
                maxtime = Draw.MainDrawer.maxTime/100
                start = max(min(0+maxtime*(zoom-1)+offset*maxtime/1000, maxtime-1), 0)
                #start = int(start/100)*100
                end = max(min(maxtime-maxtime*(zoom-1)+offset*maxtime/1000, maxtime), 1)
                #end = int(end/100)*100
                steps = []
                userline = []
                data = []
                #qrys = []

                samples = 2

                for step in range(0, int(samples*Draw.MainDrawer.resolution[0])):
                    index = start + step*(end-start)/(Draw.MainDrawer.resolution[0] * samples)
                    try:

                        data.append(database.normDataPerUser[userID-1][(int(index))])
                    except:
                        print "data too big "+str(step)

                # while len(steps)>0:
                #     qry = "select * from normaltable where user="+str(user)+" and (time="+str(end)
                #     currSteps = steps[:400]
                #     steps = steps[400:]
                #     for i in range(0, len(currSteps)):
                #         qry = qry+" or time="+str(currSteps[i])
                #     qry = qry+") order by time;"
                #     qrys.append(qry)


                # for qry in qrys:
                #     result = database.executeQry(qry, True)
                #     data+=result

                v = 0
                filterWindow=30
                for i in range(0, len(data)):
                    yPosition = 0
                    for windowIndex in range(0, filterWindow):
                        try:
                            yPosition += data[i+windowIndex][3]
                        except:
                            break
                    yPosition /= filterWindow
                    userline.append((v/samples,yPosition*150+resolution[1]/7))
                    v+=1
                self.userlines.append(userline)



            # for user in self.users:
            #     userline = []
            #     count = resolution[1]
            #     lowerBound = int(count - count/zoom)
            #     upperBound = int(count/zoom)
            #     #count = upperBound-lowerBound
            #     for index in range(lowerBound, upperBound):
            #         offset = ((index-lowerBound)/float(upperBound-lowerBound))
            #         userHeadIndex = int(index*len(user.headLocations)/count)
            #         try:
            #             v = (float(user.headLocations[userHeadIndex][0]), resolution[1] * offset)
            #             userline.append(v)
            #         except:
            #             print("exception at index = " + str(index))
            #
            #
            #     self.userlines.append(userline)


            # timestamps = database.findTimestamps(1-zoom+offset, zoom+offset, resolution[1])
            #
            #
            # for userID in range(1, 4):
            #     data = []
            #     while len(timestamps) > 0:
            #         whereTimeString = ""
            #         sublist = timestamps[:500]
            #         timestamps = timestamps[500:]
            #         for time in sublist:
            #             whereTimeString = whereTimeString + " or time = " + str(time)
            #         whereTimeString = whereTimeString.replace(" or ", "", 1)
            #
            #
            #
            #         subdata = database.executeQry("select * from maintable where user = "+str(userID)+" and head = 'head' and ("+whereTimeString+")", True)
            #         data += subdata
            #     print len(data)
        colors = []
        colors.append((255,60,60))
        colors.append((60, 255,255))
        colors.append((60,60,255))
        colors.append((60,255,60))
        i=0
        for userline in self.userlines:
            #index = self.users.index(user)
            #if(len(self.userlines)>0):
            #    userline = self.userlines[index]

            color = '%02x%02x%02x' % colors[i]
            i+=1
            Draw.MainDrawer.drawPolyLine(parent, userline, color, self.lineThickness, i)
