# GIAnT

The Group Interaction Analysis Toolkit *GIAnT* is a research tool that visualizes interactions of groups of people in front of a large interactive display wall. Functionality of and rationale for GIAnT can be found in our publication:

>  Ulrich von Zadow and Raimund Dachselt. 2017. GIAnT: Visualizing Group Interaction at Large Wall Displays. In *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '17)*. ACM, New York, NY, USA, DOI: http://dx.doi.org/10.1145/3025453.3026006

Please note that this is a research prototype and therefore provided as is. Still, if you have questions or issues, please contact ulrich.zadow@tu-dresden.de. Also, not that it is licensed under the GPL (See the LICENSE file) and we would be happy to integrate code provided by others. One good way to do this is to fork using github and provide us with a pull request that we can discuss.

## Installing GIAnT

Plan some time for the installation, as the toolkit has a number of dependencies.

### Prereqisites.

GIAnT is plattform-independent and based on libavg.
We have tested it under Mac and Linux.
Still, there should be little to no OS-specific code; porting it should be a matter of adjusting the make process and possibly some minor source code changes.

So, first install the development version of libavg as detailed on one of these pages:

* Windows: https://www.libavg.de/site/projects/libavg/wiki/WinSourceInstall
* Mac: https://www.libavg.de/site/projects/libavg/wiki/MacSourceInstall
* Linux: https://www.libavg.de/site/projects/libavg/wiki/UbuntuSourceInstall

Then, install sqlite (https://sqlite.org/). This is an easy process that depends on your plattform.

### The libavg plugin

GIAnT uses a small libavg plugin to display the visualizations which is built using CMake:

```bash
$ cd GIAnT/plugin
$ mkdir build && cd build
$ cmake ..
$ make -j5
$ sudo make install
```

### External plugins

GIAnt needs two small external libavg plugins:

* PyGLM: https://github.com/imldresden/PyGLM and
* HeatMapNode: https://github.com/imldresden/HeatMapNode

Clone both repositories and build them according to the instructions there.

## Importing data

GIAnT expects its data to be in an SQLite database and provides a script to generate this database from raw csv files. You will probably need to tweak settings in setup.py and pat_model.py to get it to find your files, and, if necessary, adapt the import to your csv files.

There are currently two csv files per session, formatted as follows:

* optitrack head data: 
  * timestamp: hh:mm:ss:mil
  * userid
  * pos: (x,y,z) in meters. (0,0,0) is at the lower left corner of the wall. When facing the wall, x points left, y up, z into the wall.
  * rot: (yaw, pitch, roll) angle in radians. Angles are applied in this order. Origin is facing the wall.
  
```csv
"timestamp","id","pos","rot"
"15:24:36.685","1","(-2.7256436347961426, 1.3635157346725464, -1.8309845924377441)","(0.21834592521190643, -0.7315365076065063, 0.20152150094509125)"
"15:24:36.686","1","(-2.7256436347961426, 1.3635157346725464, -1.8309845924377441)","(0.21834592521190643, -0.7315365076065063, 0.20152150094509125)"
"15:24:36.686","1","(-2.7256436347961426, 1.3635157346725464, -1.8309845924377441)","(0.21834592521190643, -0.7315365076065063, 0.20152150094509125)"
```
  
* touch data:
  * timestamp: hh:mm:ss:mil
  * (x,y): position in pixels
  * id: String identifier of the user

```csv
"timestamp","pos","userid"
"15:25:16.947","(6365,1501)","1"
"15:25:18.447","(5387,1804)","2"
"15:25:18.447","(5372,1839)","None"
```

Run the import script:

```
$ ./setup.py
```

GIAnt also expects a video file for each session. This video file should be coded so that it contains no delta frames, e.g. by running it through ffmpeg or avconv:

```
$ avconv -i 2016.03.17-151215-input.mp4 -vcodec h264 -g 1 2016.03.17-151215-output.h264
```

The timestamp in the video filename is used for synchronization with the motion and touch data, so it's best to generate the video file name automatically.

## Starting  GIAnT

```
$ python main.py
```
