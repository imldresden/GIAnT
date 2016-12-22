# GIAnT

The Group Interaction Analysis Toolkit *GIAnT* is a research tool that visualizes interactions of groups of people in front of a large interactive display wall. Functionality of and rationale for GIAnT can be found in our publication:

>  Ulrich von Zadow and Raimund Dachselt. 2017. GIAnT: Visualizing Group Interaction at Large Wall Displays. In *Proceedings of the SIGCHI Conference on Human Factors in Computing Systems (CHI '17)*. ACM, New York, NY, USA, DOI: http://dx.doi.org/10.1145/3025453.3026006

Please note that this is a research prototype and therefore provided as is. Still, if you have questions or issues, please contact ulrich.zadow@tu-dresden.de. Also, although it is licensed under a permissive 3-clause BSD license (See the LICENSE file), we would be happy to integrate code provided by others. One good way to do this is to fork using github and provide us with a pull request that we can discuss.

## Installing GIAnT

Plan some time for the installation, as the toolkit has a number of dependencies.

### Prereqisites.

GIAnT is plattform-independent and based on libavg. It also uses sqlite. 

So, first install the development version of libavg as detailed on one of these pages:

* Windows: https://www.libavg.de/site/projects/libavg/wiki/WinSourceInstall
* Mac: https://www.libavg.de/site/projects/libavg/wiki/MacSourceInstall
* Linux: https://www.libavg.de/site/projects/libavg/wiki/UbuntuSourceInstall

Then, install sqlite (https://sqlite.org/). This is an easy process that depends on your plattform.

### The libavg plugin

GIAnT uses a small libavg plugin to display the visualizations which is built using CMake:


```bash
$ cd GIAnT/plugin
$ mkdir build
$ cmake ..
$ make
$ sudo make install
```

## Importing data

GIAnT expects its data to be in an SQLite database and provides a script to generate this database from raw csv files. You will probably need to tweak settings in setup.py and pat_model.py to get it to find your files, and, if necessary, adapt the import to your csv files.

There are currently two csv files per session, formatted as follows:

* optitrack head data: 
  * timestamp: hh:mm:ss:mil
  * userid
  * pos: (x,y,z) in meters
  * rot: (a,b,c,d) quaternion
* touch data:
  * timestamp: hh:mm:ss:mil
  * (x,y): position in pixels
  * id: String identifier of the user

Run the import script:

```
$ ./setup.py
```

GIAnt also expects a video file for each session. This video file should be coded so that it contains no delta frames, e.g. by running it through ffmpeg or avconv:

```
$ avconv -i 2016.03.17-151215-input.mp4 -vcodec h264 -g 1 2016.03.17-151215-output.h264
```

The timestamp in the video filename is used for synchronization with the motion and touch data.

## Starting  GIAnT

```
./start.py
```
