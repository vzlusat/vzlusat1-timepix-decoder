# xray-decoder - Utility for decoding VZLUSAT-1 X-ray images

## Prerequisities

Running the **decoder** on Linux requires installing python and matplotlib on both Linux and Windows. Follow these instructions:

### Linux

Install python and matplotlib by running:

```bash
sudo apt-get install python2.7-dev python-matplotlib python3-pip python3-tk python-pmw python-pip python-mpltoolkits.basemap
```

### Windows

1. Install the latest Python3 from the website: https://www.python.org/downloads/
2. Install Visual C++ Build tools 2015 from: http://landinghub.visualstudio.com/visual-cpp-build-tools
3. Install Anaconda: https://www.continuum.io/downloads
4. Run Anaconda Prompt, new installed program a ```input conda install -c conda-forge basemap```
2. Run "run_as_admin.bat" script as Administrator (right click on it and click on "Run as administrator").
Doing this is neccessary just for the first time (it installs required library).
After that, double-clicking decoder.py should be sufficient.

## Running the decoder

## Linux

Open a Terminal window and run followoing command in the directory of the decoder:

```bash
python decoder.py
```

## Windows

Doubleclick the **decoder.py** file.

