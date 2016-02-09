from libavg import app
from Draw import main_drawer
import Options
import F_Formations
import Video

"""start parameter"""
Options.SHOW_F_FORMATIONS = True
Options.LOAD_F_FORMATIONS = False
Options.COLOR_SCHEME = 0
F_Formations.DURATION = 5000
F_Formations.DISTANCE = 150
F_Formations.ANGLE = 100
F_Formations.MOVEMENT = 50

Video.path = "csv/M2U00003.MPG"

app.App().run(main_drawer(), app_resolution='1500x800')
