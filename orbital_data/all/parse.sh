#!/bin/bash

outhk="01_housekeeping.txt"
outmetadata="02_metadata.txt"
outdata="03_images.txt"

rm "$outhk" 2> /dev/null
rm "$outmetadata" 2> /dev/null
rm "$outdata" 2> /dev/null

touch "$outhk"
touch "$outmetadata"
touch "$outdata"

datadir="../all/147.228.97.106/download"

filelist=`find $datadir -type f | sort | grep txt`

for filename in $filelist;
do

  isold=$( echo "$filename" | grep old)

  if [ ! -z "$isold" ]; then

    continue

  fi

  ishkc=$( echo "$filename" | grep S1P58C)

  if [ ! -z "$ishkc" ]; then

    cat $filename | grep 13ea5a -B 4 | sed '/chunk/d' | sed '/flag/d' | sed '/adr/d' >> "$outhk"
    echo "Parsing HKC from $filename"

  fi

  ishk=$( echo "$filename" | grep S4P1C )

  if [ ! -z "$ishk" ]; then

    cat $filename | sed '/chunk/d' | sed '/flag/d' | sed '/adr/d' >> "$outhk"
    echo "Parsing HKD from $filename"

  fi

  ismetadata=$( echo "$filename" | grep S4P2C )

  if [ ! -z "$ismetadata" ]; then

    cat $filename | sed '/chunk/d' | sed '/flag/d' | sed '/adr/d' >> "$outmetadata"
    echo "Parsing metadata from $filename"

  fi

  isdata=$( echo "$filename" | grep S4P3C )

  if [ ! -z "$isdata" ]; then

    cat $filename | sed '/chunk/d' | sed '/flag/d' | sed '/adr/d' >> "$outdata"
    echo "Parsing image from $filename"

  fi

done

echo "Running postprocessing for new file format"

files=( "$outhk" "$outmetadata" "$outdata" )

for ((i=0; i < ${#files[*]}; i++));
do

  echo "Postprocessing ${files[$i]}"

  # delete the human-readible transcript at the end of the lines
  /usr/bin/vim -E -s -c '%g/^000000/norm! f|D' -c "wqa" -- "${files[$i]}"

  # convert the "up-to" three lines to a single line
  /usr/bin/vim -E -s -c '%g/^00000040/norm! ^daW^d$k$p' -c "wqa" -- "${files[$i]}"
  /usr/bin/vim -E -s -c '%g/^00000020/norm! ^daW^d$k$p' -c "wqa" -- "${files[$i]}"
  /usr/bin/vim -E -s -c '%g/^00000000/norm! ^daW:s/ //gIdata: Otime: 0000000000 0 0' -c "wqa" -- "${files[$i]}"

  # delete the empty lines
  /usr/bin/vim -E -s -c '%g/^$/norm! "_dd' -c "wqa" -- "${files[$i]}"
  # substitute every double space for single space
  /usr/bin/vim -E -s -c '%s/\s\+/ /g' -c "wqa" -- "${files[$i]}"
  # remove abundant endlns
  /usr/bin/vim -E -s -c '%s/$//g' -c "wqa" -- "${files[$i]}"
  # remote "--" lines
  /usr/bin/vim -E -s -c '%g/^--$/norm! dd' -c "wqa" -- "${files[$i]}"

  mv "${files[$i]}" ../
done

echo Done
