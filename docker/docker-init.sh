#!/bin/bash

while true; do
    flask initdb
    if [[ "$?" == "0" ]]; then
        break
    fi
    time=$(date "+%Y-%m-%d %H:%M:%S")
    echo $time " Initdb command failed, retrying in 5 secs..."
    sleep 5
done