#!/usr/bin/env bash
while true; do
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo "[Updater] Online service detected!"
        sleep 1800
    else
        sleep 30
    fi
done
