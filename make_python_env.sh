#!/bin/bash

sudo apt-get -y install python3-venv
sudo apt-get -y install python3-pip

python3 -m venv python_env

source ./python-env/bin/activate

pip3 install wheel
pip3 install matplotlib
pip3 install tk
pip3 install pmw
pip3 install cartopy
pip3 install scipy
pip3 install ephem
