#!/bin/bash

# get the path to this script
MY_PATH=`dirname "$0"`
MY_PATH=`( cd "$MY_PATH" && pwd )`

cd $MY_PATH/..

# rsync pngs
rsync -vPr images_png/* /media/google-drive/VZLUSat/orbital_data/png/

# rsync csv
rsync -vPr images_csv/* /media/google-drive/VZLUSat/orbital_data/csv/
