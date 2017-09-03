#!/bin/bash

version="1.0.15"

files=(
"colormaps.txt"
"comments.txt"
"decoder.py"
"orbital_data"
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
  cp -r ${files[$i]} $DIR_NAME/.
done

# clean all .pyc files
rm $DIR_NAME/**/**.pyc
rm -rf $DIR_NAME/src/__pycache__

# create the zip file
zip -r $DIR_NAME.zip $DIR_NAME

# remove the dirctory
rm -rf $DIR_NAME
