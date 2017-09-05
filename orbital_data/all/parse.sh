outhkc="00_hkc.txt"
outhk="01_housekeeping.txt"
outmetadata="02_metadata.txt"
outdata="03_images.txt"

rm "$outhkc" 2> /dev/null
rm "$outhk" 2> /dev/null
rm "$outmetadata" 2> /dev/null
rm "$outdata" 2> /dev/null

touch "$outhkc"
touch "$outhk"
touch "$outmetadata"
touch "$outdata"

datadir="../all/147.228.97.106/download"

for filename in `find $datadir -type f | sort -n -k7.4`;
do

  echo "Parsing file $filename"

  istxt=`echo "$filename" | grep txt`

  if [ ! -z "$istxt" ]; then

    cat $filename | grep 13ea5a -A 1 -B 4 >> "$outhkc"

    ishk=`echo "$filename" | grep S4P1`

    if [ ! -z "$ishk" ]; then

      cat $filename >> "$outhk"

    fi 

    ismetadata=`echo "$filename" | grep S4P2`

    if [ ! -z "$ismetadata" ]; then

      cat $filename >> "$outmetadata"

    fi 

    isdata=`echo "$filename" | grep S4P3`

    if [ ! -z "$isdata" ]; then

      cat $filename >> "$outdata"

    fi 

  fi

done

mv "$outhkc" ../
mv "$outhk" ../
mv "$outmetadata" ../
mv "$outdata" ../
