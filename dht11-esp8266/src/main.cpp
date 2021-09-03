#include <Arduino.h>
#include <DHT.h>
#include <DHT_U.h>
#include <Adafruit_Sensor.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "wifi.h"

#define DHTpin 14 // D5 of NodeMCU is GPIO14

#define DHTTYPE DHT11 // DHT 11

DHT dht(DHTpin, DHTTYPE);

const char* mqtt_server = "10.0.0.53";

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  start(); // in wifi.h 
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Ignore messages that start with a '!'
  if ((char)payload[0] == '!') {
    return;
  }
  Serial.printf("Message arrived [%s] ", topic);
  
  String msg = "";

  for (unsigned int i = 0; i < length; i++) {
    // Serial.print((char)payload[i]);
    msg = msg + (char)payload[i];
  }
  Serial.println(msg);

  if (String(topic) == "tempSens/temp") {

    // client.publish("tempSens/temp/val", "temp");
  }

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-" + WiFi.macAddress();
    // clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("esp8266", "hello world");
      // ... and resubscribe
      client.subscribe("esp8266");
      client.subscribe("tempSens/temp");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  String newHostname = WiFi.hostname();
  newHostname.replace("ESP", "MQTT"); // "MQTT-last6MacDigits"
  WiFi.hostname(newHostname);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  dht.begin();
}

unsigned long previousMillis = 0; // millis();
bool ledOn = false;

void loop() {
  if (!client.connected()) {
    reconnect();
    /*
    Serial.println(msg);
    client.publish("esp8266", msg);
    */
  }

  client.loop();
  httpServer.handleClient();

/*
  float temp = dht.readTemperature();

    if (isnan(temp)) {
      Serial.println("temp is nan");
      return;
    }

    Serial.printf("Temp: %f\n", temp);
    */

   unsigned long currentMillis = millis();
   if ((currentMillis - previousMillis) > 4000) {
     previousMillis = currentMillis;

     if (ledOn) {
       ledOn = false;
       digitalWrite(13, LOW);
     } else {
       digitalWrite(13, HIGH);
       ledOn = true;
     }
   }
   
}