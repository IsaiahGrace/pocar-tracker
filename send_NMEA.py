from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import json
import os
import sys

logpath = '/home/pi/logs/location.log'
sentlogpath = '/home/pi/logs/sentLocations.log'
lastTxTime = time.time()
timeout = 5 * 60 # this is the maximum time before we will try to send another MQTT packet

host = "a20it8ieztmqcu-ats.iot.us-east-2.amazonaws.com"
rootCAPath = "/home/pi/aws_connect/root-CA.crt"
certificatePath = "/home/pi/aws_connect/40862_rpi.cert.pem"
privateKeyPath = "/home/pi/aws_connect/40862_rpi.private.key"
clientId = "40862_rpi"
port = 8883

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

def send_data():
    global lastTxTime

    # Update lastTxTime
    lastTxTime = time.time()

    # Check our internet connection
    # Ping AWS four times with a deadline of 6 seconds, output to null
    if os.system("ping amazonaws.com -c 4 -w 6 > /dev/null 2>&1") != 0:
        print("Warning: No internet conection: " + time.ctime())
        return
    
    data = []
    
    ## build message
    with open(logpath, "r") as inFile:
        for line in inFile:
            data.append(line)

    # Clear sent locations from buffer
    open(logpath, 'w').close()

    if not data:
        return

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - send_NMEA - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    
    # Init AWSIoTMQTTClient
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
    
    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    
    print("connecting to AWS MQTT")
    # Connect and subscribe to AWS IoT
    myAWSIoTMQTTClient.connect()

    print("Connected")

    messageJson = json.dumps({
        'message' : data
    })
    
    print("JSON message:")
    print(messageJson)
    
    myAWSIoTMQTTClient.publish("iot/topic", messageJson, 1)
    myAWSIoTMQTTClient.disconnect()

    # Append sent locations 
    with open(sentlogpath,"a") as f:
        for loc in data:
            f.write(loc)
    
while(True):
    infoLoc = os.stat(logpath)
    now = time.time()
    if infoLoc.st_size < 1000 and now - lastTxTime < timeout:
        print('Waiting for NMEA data. Timeout remaining: ' + str(timeout - int(now - lastTxTime)) + " location.log size: " + str(infoLoc.st_size) + " : " + time.ctime())
    else:
        try:
            send_data()
        except Exception as e:
            if type(e) == KeyboardInterrupt:
                raise(e)
            print(type(e))
            print(e)

    sys.stdout.flush()
    time.sleep(11)
