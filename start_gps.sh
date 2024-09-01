#!/bin/bash

# Function to set permissions
set_permissions() {
    sudo chmod 666 /dev/ttyAMA0
}

# Set initial permissions
set_permissions

# Continuously run the cat command and redirect output to a temp file
while true; do
    set_permissions
    cat /dev/ttyAMA0 > /tmp/gps_data.txt
    sleep 1
done