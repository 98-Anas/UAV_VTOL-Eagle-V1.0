#!/bin/bash

clear

echo "Running vtol mission 2 system"

sleep 2

echo "Starting GPS..."

./start_gps.sh &

sleep 2

echo "system initialization..."

sleep 2

python vid_gps.py &


