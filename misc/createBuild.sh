#!/bin/bash

version="1.0.21"

files=(
"colormaps.txt"
"comments.txt"
"decoder.py"
"favorites.py"
"orbital_data"
"processing"
"README.md"
"run_as_admin.bat"
"settings.txt"
"src"
"tle.txt"
)

# get the path to this script
MY_PATH=`dirname "$0"`
MY_PATH=`( cd "$MY_PATH" && pwd )`

cd $MY_PATH/..

# create the directory for the build
DIR_NAME="xray-decoder-$version"
rm -rf $DIR_NAME
mkdir $DIR_NAME

# copy files
for ((i=0; i < ${#files[*]}; i++));
do
  cp -r -L ${files[$i]} $DIR_NAME/.
done

# clean all .pyc files
rm $DIR_NAME/**/**.pyc
rm -rf $DIR_NAME/src/__pycache__
rm -rf $DIR_NAME/orbital_data/all

# create the zip file
zip -r $DIR_NAME.zip $DIR_NAME

# remove the dirctory
rm -rf $DIR_NAME
