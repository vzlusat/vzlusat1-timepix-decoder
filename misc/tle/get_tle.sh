TLE_DIR="147.228.97.106/tle"

# get the path to this script
MY_PATH=`dirname "$0"`
MY_PATH=`( cd "$MY_PATH" && pwd )`

wget -rN --no-parent --reject "index.html*" --accept "*2023*" http://147.228.97.106/tle/

cd $MY_PATH/$TLE_DIR
rm _amateur.txt
rm _cubesat.txt

for filename in `ls *.txt`;
do
  tle=`cat $filename | grep "VZLUSAT-1" -A 2 | tail -2`

  if [ ! -z "$tle" ]; then

    # extract the time stamp from the file name
    mytime=`echo "$filename" | sed 's/cubesat-//' | sed 's/active-//' | sed 's/tle-new-//' | sed 's/\.txt//'`

    # reformat the time stamp to a proper format
    correcttime=`echo "$mytime" | "$MY_PATH/vims" -s 'A|^f-lyiw$p^2f-lyiwA/p^yiwA/p^3f-lyiwA p^4f-lyiwA:p^5f-lyiwA:p^df|'`

    # convert the human readable time stamp to unix epoch
    timestamp=`date -u --date="$correcttime" +"%s"`

    echo $tle

    echo "$timestamp" >> tle.txt
    echo "$tle" >> tle.txt

  fi

done

mv tle.txt $MY_PATH/../../
