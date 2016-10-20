#include <ESP8266httpUpdate.h> // For Server OTA
#include <ESP8266WiFi.h>          //https://github.com/esp8266/Arduino

//needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>         //https://github.com/tzapu/WiFiManager

#include <SPI.h> 
#include <Wire.h>
#include "PixySPI_SS.h"
#include <WebSocketsClient.h>

uint16_t blocks;
uint16_t old_blocks;

PixySPI_SS pixy(D8);

WebSocketsClient webSocket;

int counter=0;
char buf[10];
unsigned long timedelay =0;

String macadress = "";
IPAddress ip;
String strIP;
bool wifiConnectFailed = false;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t lenght) {

    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[WSc] Disconnected!\n");
            break;
        case WStype_CONNECTED:
            {
                Serial.printf("[WSc] Connected to url: %s\n",  payload);
                webSocket.sendTXT("camera-" + macadress);
            }
            break;
        case WStype_TEXT:
            Serial.printf("[WSc] get text: %s\n", payload);

      // send message to server
      // webSocket.sendTXT("message here");
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

    // Initialize camera
    pixy.init();

    byte mac[6];
    WiFi.macAddress(mac);
    char macadd[7];
    for(int i=0; i<6; i++){
        macadd[i] = (char)mac[i];
    }
    macadress = String(macadd[0],HEX) + String(macadd[1],HEX) + String(macadd[2],HEX) + String(macadd[3],HEX) + String(macadd[4],HEX) + String(macadd[5],HEX);
    

    WiFiManager wifiManager;
          //  wifiConnectFailed = true; 
         // wifiManager.resetSettings();
    wifiManager.autoConnect("VR Tracker CAMERA", "vrtracker");
    Serial.println("Wifi connection established");

    /*char* buffer;
    ip = WiFi.localIP();
    sprintf(buffer,"%d:%d:%d:%d", ip[0],ip[1],ip[2],ip[3]);*/
    
    strIP = WiFi.gatewayIP().toString();
    Serial.println("My IP : " + WiFi.localIP().toString());
    Serial.println("Gateway IP : " + strIP);

    // Check for software update
    ESPhttpUpdate.update("http://www.julesthuillier.com/vrtracker/arduino/camera2.bin");

   
    // Start websocket client
    if(strIP == "192.168.10.1"){
      webSocket.begin(strIP, 8001);
    }
    else{
      webSocket.begin("192.168.2.12", 8001);
    }
    
    webSocket.onEvent(webSocketEvent);  
}

void loop() {
   
  webSocket.loop();
  old_blocks = blocks;
  blocks = pixy.getBlocks();
  if (blocks && (old_blocks != blocks))
  { 
      for (int j=0; j<blocks; j++)
      {  
        if(pixy.blocks[j].width < 30 && pixy.blocks[j].height < 30){
          String data = "";
          char extract[2];
          sprintf(extract, "%d", pixy.blocks[j].signature);
          data += extract;
          data += 'x';
          sprintf(extract, "%d", pixy.blocks[j].x);
          data += extract;
          data += 'y';
          sprintf(extract, "%d", pixy.blocks[j].y);
          data += extract;
          data += 'h';
          sprintf(extract, "%d", pixy.blocks[j].width);
          data += extract;
          data += 'w';
          sprintf(extract, "%d", pixy.blocks[j].height);
          data += extract;
          data += 'a';
          sprintf(extract, "%d", pixy.blocks[j].angle);
          data += extract;
      //    Serial.println(data);
          webSocket.sendTXT(data);
        }
      }   
  }  
  
  else {
      delayMicroseconds(20);
  } 
  
}
