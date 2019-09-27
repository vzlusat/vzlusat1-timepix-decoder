# get th,,,ath to this script
MY_PATH=`dirname "$0"`
MY_PATH=`( cd "$MY_PATH" && pwd )`

wget -rN --no-parent -A "*S4P1C*,*S4P2C*,*S4P3C*,*S1P58C*" -R "*old*" http://147.228.97.106/download/last_xray/
