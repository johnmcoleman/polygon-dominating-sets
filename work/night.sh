#!/bin/sh
# Run the n=11 job in a bounded window: ./night.sh <procs> <stop HH:MM>.  Resumable; finished chunks are kept.
cd "$(dirname "$0")"
procs=$1; stop=$2
now=$(date +%s); end=$(date -j -f "%Y-%m-%d %H:%M" "$(date +%Y-%m-%d) $stop" +%s)
[ "$end" -le "$now" ] && end=$((end+86400))
caffeinate -i python3 launch.py 11 25 "$procs" n11a 10 >> n11a.log 2>&1 &
( sleep $((end-now)); pkill -f "launch.py 11 25"; pkill -f pathdp3_6; echo "window closed $(date)" >> n11a.log ) &
wait
