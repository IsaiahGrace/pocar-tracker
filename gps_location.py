'''
This is the script that collects the NMEA data from the L96 module, filters it, and writes it to a log file
'''

from tracker import tracker
from time import sleep, time
import sys

def main():
    node = tracker.Tracker()
    print("reset L96")
    node.resetL96()

    msgRMC = ""
    msgGGA = ""
    logData = ""
    altitude = "x" # Initial altitude unkown
    while (True):
        startTime = time()
        gps_message = node.readNMEA()
        if gps_message == None:
            print("readNMEA() returned None")
            sleep(1)
            continue

        # Decode the message into a string and then split it into an array.
        msg = gps_message.decode(encoding="utf-8", errors='ignore').split("$")
        
        for line in msg:
            # Filter out empty lines
            if line == None:
                continue
            
            # Filter out lines that are not RMC or GGA
            if line[2:5] != "RMC" and line[2:5] != "GGA":
                continue

            # For debug, print the line
            #print("RAWDATA - $" + line,end='')
            
            # Deal wiht RMC
            if line[2:5] == "RMC":
                msgRMC = line.split(',')
                
                # Filter out corrupted RMC packets
                if len(msgRMC) != 14:
                    continue

                # Filter out RMC packets without actual data
                if msgRMC[2] != "A":
                    continue

                # If we've made it this far, then the RMC data is worth logging
                logData = line[0:-2] + ","

            # Deal with GGA
            if line [2:5] == "GGA":
                msgGGA = line.split(',')

                # Filter out corrupted GGA packets
                if len(msgGGA) != 15:
                    continue
                
                # Filter out GGA without actual data
                if msgGGA[6] == "0":
                    continue
                
                altitude = msgGGA[9]
                
        # This will allow us to use the LAST RMC + GGA, so only print one RMC for every 10 seconds
        if logData != "":
            print("$" + logData + altitude)
            with open('/home/pi/logs/location.log','a') as f:
                f.write("$" + logData + altitude + "\r\n")

        while(time() - startTime < 5):
            sleep(0.5)
            
                        
while(True):
    try:
        main()        
    except Exception as e:
        if (type(e) == KeyboardInterrupt):
            raise(e)
        if (type(e) == ValueError):
            raise(e)
        print(type(e))
        print(e)
        sleep(1)
