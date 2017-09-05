outputfile="00_hkc.txt"

rm "$filename" 2> /dev/null
touch "$outputfile"

datadir="../all/147.228.97.106/download"

for filename in `find $datadir -type f`;
do

  istxt=`echo "$filename" | grep txt`

  if [ ! -z "$istxt" ]; then

    cat $filename | grep 13ea5a -A 1 -B 4 >> "$outputfile"

  fi

done

mv "$outputfile" ../
