#!/bin/sh
# Chain of long runs (owner away 2026-11-19 for a week).  Safe to re-run: every stage is resumable
# and skipped when its result exists.   nohup ./queue.sh > queue.log 2>&1 &
cd "$(dirname "$0")"
P=16
[ -f result_n11a.txt ] || caffeinate -i python3 launch.py 11 25 $P n11a 10 >> n11a.log 2>&1
[ -f result_d11a.txt ] || caffeinate -i python3 launch2.py dom 11 25 $P d11a 10 >> d11a.log 2>&1
[ -f result_n12a.txt ] || caffeinate -i python3 launch2.py tds 12 25 $P n12a 10 >> n12a.log 2>&1
[ -f result_d12a.txt ] || caffeinate -i python3 launch2.py dom 12 25 $P d12a 10 >> d12a.log 2>&1
