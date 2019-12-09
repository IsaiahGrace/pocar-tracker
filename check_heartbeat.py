from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import json
import os
import sys

heartpath = '/home/pi/logs/heartbeat_request.log'

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------")
    sys.stdout.flush()
    with open(heartpath, 'w') as f:
        f.write(json.loads(message.payload)['message'])

host = "a20it8ieztmqcu-ats.iot.us-east-2.amazonaws.com"
rootCAPath = "/home/pi/aws_connect/root-CA.crt"
certificatePath = "/home/pi/aws_connect/40862_rpi.cert.pem"
privateKeyPath = "/home/pi/aws_connect/40862_rpi.private.key"
clientId = "40862_rpi"
topic = "iot/heartbeat_request"
port = 8883

while (True):
    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - ckeck_heartbeat - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    
    # Init AWSIoTMQTTClient
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, cleanSession=False)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)
    
    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 60, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    
    print("connecting to AWS MQTT")
    myAWSIoTMQTTClient.connect()
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
    
    # Connect and subscribe to AWS IoT
    #uptime = 0
    #timout = 6 # x10 for roughly how many seconds to wait before disconnecting the 
    #while (uptime < timout):
    while (True):
        print("Connected: Waiting for heatbeat: " + time.ctime())
        sys.stdout.flush()
        time.sleep(10)
