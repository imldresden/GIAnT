# import libavg
from libavg import app, avg, player
from Draw import MainDrawer
# import FileLoader
# import database


# database.createMainTable()
# database.createTimeTable()
# FileLoader.loadAllFiles()
# database.insertAllTimeStamps()
# database.createNormalTable()
#
# print database.executeQry("select count(*) from normaltable;", True)

app.App().run(MainDrawer(), app_resolution='1920x1080')
