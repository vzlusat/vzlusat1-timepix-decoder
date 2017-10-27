# xray-decoder - Utility for decoding VZLUSAT-1 X-ray images

## Measurement log

  * Dosimetry 1 (the first one, a short one)
    * Image range: 405 to 416
    * Linux time range: 1503686482 to 1503698652
    * Human readible time range: 2017-08-25 18:41:22 to 2017-08-25 22:04:12
    * Exposure 1 s every 3 minutes, Full resolution
  * Dosimetry 2
    * Image range: 417 to 796
    * Linux time range: 1504123980 to 1504210199
    * Human readible time range: 2017-08-30 20:13:00 to 2017-08-31 20:09:59
    * Exposure 1 s every 3 minutes, Binning32+histograms
  * Dosimetry 3 (after the solar flare)
    * Image range: 813 to 993
    * Linux time range: 1504811904 to 1504901637
    * Human readible time range: 2017-09-07 19:18:24 to 2017-09-08 20:13:57
    * Exposure 1 s every 6 minutes, Fullres+Binning32+histograms
  * Dosimetry 4
    * Image range: 994 to 1388
    * Linux time range: 1504955284 to 1505043047
    * Human readible time range: 2017-09-09 11:08:04 to 2017-09-10 11:30:47
    * Exposure 1 s every 3 minutes, Binning32+histograms
  * Dosimetry 5
    * Image range: 1449 to 1772
    * Linux time range: 1505761088 to 1505847421
    * Human readible time range: 2017-09-18 18:58:08 to 2017-09-19 18:57:01
    * Exposure 1 s every 3 minutes, Binning32+histograms
  * Dosimetry 6
    * Image range: 1879 to 2477
    * Linux time range: 1506506834 to 1506628152
    * Human readible time range: 2017-09-27 10:07:14 to 2017-09-28 19:49:12
    * Exposure 1 s every 1 minutes, Binning16+histograms
  * Dosimetry 7
    * Image range: 2478 to 3318
    * Linux time range: 1506891603 to 1506973241
    * Human readible time range: 2017-10-01 21:00:03 to 2017-10-02 19:40:41
    * Exposure 1 s every 1 minutes, Binning16+histograms
  * Anomaly 1
    * Image range: 3319 to 3332
    * Linux time range: 1507031024 to 1507083894
    * Human readible time range: 2017-10-03 11:43:44 to 2017-10-04 02:24:54
  * Anomaly 2
    * Image range: 3333 to 3346
    * Linux time range: 1507286624 to 1507345186
    * Human readible time range: 2017-10-06 10:43:44 to 2017-10-07 02:59:46
  * Dosimetry 8
    * Image range: 3349 to 3734
    * Linux time range: 1507579978 to 1507664275
    * Human readible time range: 2017-10-09 20:12:58 to 2017-10-10 19:37:55
    * Exposure 1 s every 3 minutes, Binning16+histograms
  * Anomaly 3
    * Image range: 3735 to 3749
    * Linux time range: 1507674729 to 1507729925
    * Human readible time range: 2017-10-10 22:32:09 to 2017-10-11 13:52:05
  * Dosimetry 9
    * Image range: 3758 to 4240
    * Linux time range: 1508187623 to 1508267232
    * Human readible time range: 2017-10-16 21:00:23 to 2017-10-17 19:07:12
    * Exposure 1 s every 2 minutes, Binning16+histograms
  * Dosimetry 10
    * Image range: 4245 to 4846
    * Linux time range: 1508924942 to 
    * Human readible time range: 2017-10-25 09:49:02 to 
    * Exposure 1 s every 2 minutes, Binning16+histograms

# Installation

## Prerequisities

Running the **decoder** on Linux requires installing python libraries on both Linux and Windows.
Thought, it is much easier to run it on Linux...
Follow these instructions:

### Linux

Install python and matplotlib by running:

```bash
sudo apt-get install python2.7-dev python-matplotlib python3-pip python3-tk python-pmw python-pip python-mpltoolkits.basemap python3-mpltoolkits.basemap python-scipy
```

### Windows

1. Install the latest Python3 from the website: https://www.python.org/downloads/
 
If you want to have a TwoLineElements+Globus, follow the next three bullet points, otherwise skip to the point 2 and disable the globus feature in _settings.txt_. Following bullet points may take very long time on Windows...

- Install Visual C++ Build tools 2015 from: http://landinghub.visualstudio.com/visual-cpp-build-tools
- Install Anaconda: https://repo.continuum.io/archive/Anaconda3-4.4.0-Windows-x86_64.exe
- Run Anaconda Prompt (Start menu->Anaconda Prompt) and input following command to the command line: ```conda install -c conda-forge basemap```
 
2. Run "run_as_admin.bat" script as Administrator (right click on it and click on "Run as administrator").
Doing this is neccessary just for the first time (it installs required library).
After that, double-clicking decoder.py should be sufficient.

## Running the decoder

## Linux

Open a Terminal window and run followoing command in the directory of the decoder:

```bash
python decoder.py
```

It might be neccessary to re-run the program multiple times, before it correctly loads its libraries for the first time.

## Windows

Doubleclick the **decoder.py** file.

It might be neccessary to re-run the program multiple times, before it correctly loads its libraries for the first time.

