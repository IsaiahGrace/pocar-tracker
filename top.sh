#! /bin/bash

# This is a top level bash script that will coordinate the execution of all python scripts in the pocar tracker beacon project
EXIT_CODE=2

# disable ppp0
sudo poff
EXIT_CODE=$?

if [[ $EXIT_CODE != 0 ]] && [[ $EXIT_CODE != 1 ]] # It is okay if poff exits with code 1, this means that there was no ppp0 to stop, so nothing was done
then
    echo sudo poff exited with code $EXIT_CODE
    exit 1
fi

# M95 config
sudo -u pi python3 /home/pi/tracker_enable.py
EXIT_CODE=$?

if [[ $EXIT_CODE != 0 ]]
then
    echo python3 /home/pi/tracker_enable.py exited with code $EXIT_CODE
    exit 1
fi

# pon and setup ppp0
sleep 2
echo Starting pon service
SUCCESS=0
TIMEOUT=0

while [[ $SUCCESS == 0 ]]
do
    echo trying to establish ppp0
    
    sudo pon
    EXIT_CODE=$?
    
    TIMEOUT=$((TIMEOUT+1))
    
    if [[ $TIMEOUT -ge 10 ]]
    then
	echo ERROR: failed to extablish ppp0
	exit 1
    fi

    sleep 2
    ping amazonaws.com -c 4 -w 6
    EXIT_CODE=$?
    
    if [[ $EXIT_CODE == 0 ]]
    then
	SUCCESS=1
	echo SUCCESS: established network connectivity
    fi
done

#exit 0

echo System configured, starting Python scripts
echo `whoami`

# start scripts in parallel
sudo -u pi python3 /home/pi/gps_location.py > /home/pi/logs/gps_location.log 2>&1 &
sudo -u pi python3 /home/pi/send_NMEA.py > /home/pi/logs/send_NMEA.log 2>&1 &
sudo -u pi python3 /home/pi/check_heartbeat.py > /home/pi/logs/check_heartbeat.log 2>&1 &
sudo -u pi python3 /home/pi/heartbeat_gpio.py > /home/pi/logs/heartbeat_gpio.log 2>&1 &
sudo -u pi python3 /home/pi/acknowledge_heartbeat.py > /home/pi/logs/acknowledge_heartbeat.log 2>&1 &

echo System up and running!!
