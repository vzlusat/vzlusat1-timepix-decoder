# get th,,,ath to this script
MY_PATH=`dirname "$0"`
MY_PATH=`( cd "$MY_PATH" && pwd )`

wget -rN --no-parent --reject 'index.html*|*.wav' http://147.228.97.106/download/

git rm ./**/*.wav
git rm ./147.228.97.106/download/old*
