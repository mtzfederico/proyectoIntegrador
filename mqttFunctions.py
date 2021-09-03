import paho.mqtt.client as mqtt

class color:
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    red = '\033[91m'
    end = '\033[0m'

latestTemp = 0

# https://stackoverflow.com/questions/38172180/what-is-the-equivalent-of-a-swift-completion-block-in-python
def defaultCallBack():
    print(color.red, "Default Callback called", color.end)

tempCallBack = defaultCallBack

def on_connect(client, userdata, flags, rc):
        if rc == 0:
                print("Connected successfuly")
                # print(userdata)
        else:
                print(f"Connected fail with code {rc}")

        # client.subscribe("esp8266")
        client.subscribe("tempSens/temp/val")

def on_message(client, userdata, msg):
    print(f"{color.blue}[{msg.topic}]{color.end} {msg.payload}")
    global latestTemp

    latestTemp = msg.payload.decode('utf-8')

    tempCallBack()

def on_publish(client, userdata, result):
    print(color.green, "data published", color.end)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

client.connect("10.0.0.53", 1883, 60)

client.loop_start()

def askForTemp():
    client.publish('tempSens/temp', payload="Hello", qos=0, retain=False)

if __name__ == "__main__":
    def actualCallback():
        print(f"[actualCallback] The value is: {latestTemp}")

    tempCallBack = actualCallback
    askForTemp()
    