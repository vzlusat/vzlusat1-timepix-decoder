# xray-decoder - Utility for decoding VZLUSAT-1 X-ray images

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
 
If you want to have a TwoLineElements+Globus, follow to point a), b) and c), otherwise skip to 2 and disable the feature in _settings.txt_. a), b) and c) may take very long time on Windows...

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

