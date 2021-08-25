#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ESP8266HTTPUpdateServer.h>

ESP8266WebServer httpServer(80);
ESP8266HTTPUpdateServer httpUpdater;

String ssid = "Toronet";
String password = "lukuli01";

void handleRoot() {
    String resp = "http://" + WiFi.localIP().toString() + "/update";

    Serial.print("Redirecting to: ");
    Serial.println(resp);

    httpServer.sendHeader("Location", resp, true);
    httpServer.send(302, "text/plain", "");
}

void handleStatus() {
    String response = "SSID: " + WiFi.SSID() + "\nRSSI: " + String(WiFi.RSSI()) + "\nMAC Address: " + String(WiFi.macAddress()) + "\ndnsIP: " + WiFi.dnsIP().toString() + "\nFreeSketchSpace: " + String(ESP.getFreeSketchSpace());
    httpServer.send(200, "text/plain", response);
}

void start() {
    MDNS.begin("esp8266-webupdate");
    httpUpdater.setup(&httpServer);
    MDNS.addService("http", "tcp", 80);

    httpServer.on("/", HTTP_GET, handleRoot);
    httpServer.on("/status", HTTP_GET, handleStatus);

    httpServer.begin();
}