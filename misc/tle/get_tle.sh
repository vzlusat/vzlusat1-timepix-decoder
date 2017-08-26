wget -rnd --no-parent --reject "index.html*" http://147.228.97.106/tle/

rm _amateur.txt
rm _cubesat.txt

touch -f tle.tle

for filename in `ls *.txt`;
do
  tle=`cat $filename | grep VZLUSAT -A 2 | tail -2`

  if [ ! -z "$tle" ]; then

    # extract the time stamp from the file name
    mytime=`echo "$filename" | sed 's/cubesat-//' | sed 's/\.txt//'`

    # reformat the time stamp to a proper format
    correcttime=`echo "$mytime" | vims -s 'A|^f-lyiw$p^2f-lyiwA/p^yiwA/p^3f-lyiwA p^4f-lyiwA:p^5f-lyiwA:p^df|'`

    # convert the human readible time stamp to unix epoch
    timestamp=`date -u --date="$correcttime" +"%s"`

    echo "$timestamp" >> tle.tle
    echo "$tle" >> tle.tle

  fi

done

rm *.txt

mv tle.tle tle.txt
