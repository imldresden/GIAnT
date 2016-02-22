from libavg import app
from Draw import main_drawer
import Options
import F_Formations
import Video

"""start parameter"""
Options.SHOW_F_FORMATIONS = False
Options.LOAD_F_FORMATIONS = True
Options.COLOR_SCHEME = 0
F_Formations.DURATION = 4000
F_Formations.DISTANCE = 80
F_Formations.MAX_DRIFT = 55
F_Formations.ANGLE = 90

Video.path = "csv/M2U00003.MPG"

app.App().run(main_drawer(), app_resolution='1920x1080')
