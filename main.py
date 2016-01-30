from libavg import app
from Draw import main_drawer
import Options

Options.SHOW_F_FORMATIONS = False

app.App().run(main_drawer(), app_resolution='1500x800')
