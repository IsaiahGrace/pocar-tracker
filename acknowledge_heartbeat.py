'''
This file reads heartbeat_acknowledge.log and publishes an MQTT message accordingly
'''
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import json
import os
import sys

logpath = '/home/pi/logs/heartbeat_acknowledge.log'


# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    
def send_data():
    data = list()
    ## build message
    with open(logpath, "r") as inFile:
        data = inFile.readlines()[0]

    host = "a20it8ieztmqcu-ats.iot.us-east-2.amazonaws.com"
    rootCAPath = "/home/pi/aws_connect/root-CA.crt"
    certificatePath = "/home/pi/aws_connect/40862_rpi.cert.pem"
    privateKeyPath = "/home/pi/aws_connect/40862_rpi.private.key"
    clientId = "40862_rpi"
    port = 8883

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - acknowledge_heartbeat - %(name)s - %(levelname)s - %(message)s')
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

    print(messageJson)
    myAWSIoTMQTTClient.publish("iot/heartbeat_acknowledge", messageJson, 1)

    myAWSIoTMQTTClient.disconnect()
    
    # Clear sent locations from buffer
    open(logpath, 'w').close()

while(True):
    infoLoc = os.stat(logpath)
    if infoLoc.st_size == 0:
        print('heartbeat_acknowledge.log is empty: ' + time.ctime())
        sys.stdout.flush()
    else:
        send_data()
    time.sleep(10)
