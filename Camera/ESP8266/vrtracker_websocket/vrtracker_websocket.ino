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

void webSocketEvent(WStype_t type, uint8_t * payload, size_t lenght) {

    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[WSc] Disconnected!\n");
            break;
        case WStype_CONNECTED:
            {
                Serial.printf("[WSc] Connected to url: %s\n",  payload);
                webSocket.sendTXT("camera");
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

     pinMode(D8,OUTPUT);
    Serial.println("VR Tracker by Jules Thuillier");
    pixy.init();

Serial.println(pixy.setLED(4,250,1));
 //pixy.getWord(); 
  delay(200);
  Serial.println(pixy.setBrightness(255));
  Serial.println(pixy.getBlocks());
  
     delay(200);
  


    //WiFiManager
    //Local intialization. Once its business is done, there is no need to keep it around
    WiFiManager wifiManager;
    //reset saved settings
 //   wifiManager.resetSettings();
    
    //fetches ssid and pass from eeprom and tries to connect
    //if it does not connect it starts an access point with the specified name
    //here  "AutoConnectAP"
    //and goes into a blocking loop awaiting configuration
    wifiManager.autoConnect("VR Tracker CAMERA", "vrtracker");

    //if you get here you have connected to the WiFi
    Serial.println("Wifi connection established");

    ESPhttpUpdate.update("159.203.8.64", 80, "/vrtracker/vrtracker.bin");

    webSocket.begin("192.168.1.102", 8001);
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
        
        
     //   if(pixy.blocks[j].width < 30 && pixy.blocks[j].height < 30){
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
          Serial.println(data);
          webSocket.sendTXT(data);
       // }
      }   
  }  
  
  else {
      delayMicroseconds(20);
  } 
  
}
