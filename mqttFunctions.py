"""
    mqttFunctions.py

    This is file contains the MQTT functions.
    It is imported in some files.
"""

import paho.mqtt.client as mqtt
import credentials

# Colors used for printing
class color:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'

latestTemp = 0

# https://stackoverflow.com/questions/38172180/what-is-the-equivalent-of-a-swift-completion-block-in-python
def defaultCallBack(payload=""):
    print(color.red, "Default Callback called", color.end)

# temCallBack is the callback called when the temperature sensor returns a value
tempCallBack = defaultCallBack

# temCallBack is the callback called when the web server receives something via MQTT
serverReceivedCallback = defaultCallBack

# MQTT on connect callback function
def on_connect(client, userdata, flags, rc):
        if rc == 0:
                print(color.blue, "MQTT Connected successfuly", color.end)
                # print(userdata)
        else:
                print(f"{color.red}MQTT Connection failed with code:{color.end} {rc}")

        # client.subscribe("esp8266")
        client.subscribe("tempSens/temp/val")
        client.subscribe("server/receive")

# MQTT on message received callback function
def on_message(client, userdata, msg):
    if msg.topic == "server/receive":
        serverReceivedCallback(msg.payload.decode('utf-8'))
        return

    print(f"{color.blue}[{msg.topic}]{color.end} {msg.payload}")
    global latestTemp

    latestTemp = msg.payload.decode('utf-8')

    tempCallBack()

# MQTT on message sent callback function
def on_publish(client, userdata, result):
    print(color.green, "data published", color.end)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

client.connect(credentials.MQTTServerIP, credentials.MQTTServerPort, 60)

client.loop_start()

# Function to ask the temperature sensor for the temperature
def askForTemp():
    client.publish('tempSens/temp', payload="Hello", qos=0, retain=False)

# Function to send data to the web server via MQTT
def sendToServer(payload):
    client.publish('server/receive', payload=f"{payload}", qos=2, retain=False)

# Function to change the light color
def changeLightColor(r, g, b, id):
    client.publish(f'light/{id}', payload=f"{r},{g},{b}", qos=1, retain=False)

if __name__ == "__main__":
    def actualCallback():
        print(f"[actualCallback] The value is: {latestTemp}")

    tempCallBack = actualCallback
    askForTemp()

    # sendToServer("type,notificationType,optionalMessage,alarmDate")
    