'''
Isaiah Grace

This script manages the heatbeat GPIO
'''
import RPi.GPIO as GPIO
import time
import sys

USER_BUTTON = 21 
USER_LED = 20

requestpath = "/home/pi/logs/heartbeat_request.log"
ackpath = "/home/pi/logs/heartbeat_acknowledge.log"

active_request = 0
def flickerLED():
    GPIO.output(USER_LED, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(USER_LED, GPIO.LOW)
    
def user_button_press(channel):
    global active_request
    print("User button press: " + time.ctime())
    print("heartbeat number: " + str(active_request))
    sys.stdout.flush()

    flickerLED()

    if active_request == 0:
        return

    with open(ackpath, 'w+') as f:
        f.write(str(active_request))
        
    with open(requestpath, 'w+') as f:
        f.close()
        
    active_request = 0
    
GPIO.setmode(GPIO.BCM)

GPIO.setup(USER_BUTTON, GPIO.IN)
GPIO.add_event_detect(USER_BUTTON, GPIO.FALLING, callback=user_button_press, bouncetime=300)

GPIO.setup(USER_LED, GPIO.OUT)

flickerLED()

sleeptime = 10
lines = []
while(True):
    try:
        time.sleep(sleeptime)
        if active_request == 0:
            print("checking heartbeat request " + time.ctime())
            sys.stdout.flush()
            # read the request file
            with open(requestpath, "r") as f:
                lines = f.readlines()

        if len(lines) == 0:
            GPIO.output(USER_LED, GPIO.LOW)
            active_request = 0
            sleeptime = 10
        else:
            if GPIO.input(USER_LED) == GPIO.HIGH:
                GPIO.output(USER_LED, GPIO.LOW)
            else:
                GPIO.output(USER_LED, GPIO.HIGH)
            active_request = int(lines[0])
            sleeptime = 1
            
    except Exception as e:
        if type(e) == KeyboardInterrupt:
            raise(e)
        print(type(e))
        print(e)
        sleeptime = 10
    

