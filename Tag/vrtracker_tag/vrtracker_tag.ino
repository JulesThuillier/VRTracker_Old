#include <ESP8266httpUpdate.h> // For Server OTA
#include <ESP8266WiFi.h>          //https://github.com/esp8266/Arduino

//needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>         //https://github.com/tzapu/WiFiManager
#include <WebSocketsClient.h>

WebSocketsClient webSocket;

const int led_Red_pin = D3;
const int led_Green_pin = D3;
const int led_Blue_pin = D3;
const int led_Ir_pin = D3;
const int battery_Reading = D3;

String macadress = "";

void webSocketEvent(WStype_t type, uint8_t * payload, size_t lenght) {

    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[WSc] Disconnected!\n");
            break;
        case WStype_CONNECTED:
            {
                Serial.printf("[WSc] Connected to url: %s\n",  payload);
                webSocket.sendTXT("tag-"+macadress);
            }
            break;
        case WStype_TEXT:
            Serial.printf("[WSc] get text: %s\n", payload);
            

            break;
        case WStype_BIN:
            Serial.printf("[WSc] get binary lenght: %u\n", lenght);
            hexdump(payload, lenght);

            // send data to server
            // webSocket.sendBIN(payload, lenght);
            break;
    }
}


void setup() {
  // put your setup code here, to run once:
    Serial.begin(115200);
    Serial.println("VR Tracker by Jules Thuillier");

    pinMode(led_Red_pin, OUTPUT);
    pinMode(led_Green_pin, OUTPUT);
    pinMode(led_Blue_pin, OUTPUT);
    pinMode(led_Ir_pin, OUTPUT);
    pinMode(battery_Reading, INPUT);
     
    //WiFiManager
    //Local intialization. Once its business is done, there is no need to keep it around
    WiFiManager wifiManager;
    //reset saved settings
 //   wifiManager.resetSettings();
    
    //fetches ssid and pass from eeprom and tries to connect
    //if it does not connect it starts an access point with the specified name
    //here  "AutoConnectAP"
    //and goes into a blocking loop awaiting configuration
    wifiManager.autoConnect("VR Tracker TAG", "vrtracker");
    Serial.println("Wifi connection established");

    byte mac[6];
    WiFi.macAddress(mac);
    char macadd[7];
    for(int i=0; i<6; i++){
        macadd[i] = (char)mac[i];
    }
    macadress = String(macadd[0],HEX) + String(macadd[1],HEX) + String(macadd[2],HEX) + String(macadd[3],HEX) + String(macadd[4],HEX) + String(macadd[5],HEX);


    // Check for software update
    ESPhttpUpdate.update("217.160.118.35", 80, "/vrtracker/arduino/tag.bin");

    // Start websocket client
    webSocket.begin("192.168.1.102", 8001);
    webSocket.onEvent(webSocketEvent);  
}

void loop() {
  webSocket.loop();
}

void light_off(){
}

void light_offon(uint16_t delay){

}

void light_on(){
}

void rgb(uint8_t r, uint8_t g, uint8_t b){

  
}

