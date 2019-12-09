'''
Isaiah Grace

This script enables the power supply to the Tracker HAT and boot up the M95 module
'''

from tracker import tracker
from time import sleep

def startup():
    node = tracker.Tracker()
    node.disable()
    sleep(2)
    node.enable()
    sleep(2)
    node.powerUp()
    sleep(1)
    
enabled = False
while(not enabled):
    try:
        startup()
        enabled = True
    except KeyboardInterrupt as e:
        raise(e)
    except Exception as e:
        print("tracker_enable had an exception!")
        print(type(e))
        print(e)
        print("Backing off before retrying")
        sleep(2)
        
