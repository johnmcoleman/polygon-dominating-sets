#!/bin/sh
# Chain of long runs.  Safe to re-run: every stage is resumable and skipped when its result exists.
cd "$(dirname "$0")"
while pgrep -f "launch.py 11 25 14 n11a" >/dev/null; do sleep 60; done
[ -f result_n11a.txt ] || caffeinate -i python3 launch.py 11 25 14 n11a 10 >> n11a.log 2>&1
[ -f result_n12a.txt ]  || caffeinate -i python3 launch2.py tds 12 25 14 n12a 10  >> n12a.log 2>&1
[ -f result_d11a.txt ]  || caffeinate -i python3 launch2.py dom 11 25 14 d11a 10  >> d11a.log 2>&1
[ -f result_d12a.txt ]  || caffeinate -i python3 launch2.py dom 12 25 14 d12a 10  >> d12a.log 2>&1
