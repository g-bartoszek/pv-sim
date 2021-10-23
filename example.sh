#!/bin/bash

python src/pv_sim/app.py -o test_output &
PID=$!
python src/meter/app.py -s "2020-01-01 00:00:00" -e "2020-01-02 00:00:00" -i 00:00:10
kill -9 $PID