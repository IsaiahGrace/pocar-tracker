'''
Isaiah Grace

This script disables the power supply to the Tracker HAT

'''

from tracker import tracker
from time import sleep

node = tracker.Tracker()
node.disable()
sleep(2)
