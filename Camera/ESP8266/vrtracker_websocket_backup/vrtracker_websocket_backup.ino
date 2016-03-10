#include <ESP8266httpUpdate.h> // For Server OTA
#include <ESP8266WiFi.h>          //https://github.com/esp8266/Arduino

//needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>         //https://github.com/tzapu/WiFiManager

#include <SPI.h> 
#include <Wire.h>
#include <Pixy.h>
#include "PixySPI_SS.h"
#include <WebSocketsServer.h>

uint16_t blocks;
uint16_t old_blocks;

//PixySPI_SS pixy(D8);
Pixy pixy;

WebSocketsServer webSocket = WebSocketsServer(81);

int counter=0;

char buf[10];
unsigned long timedelay =0;

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t lenght) {

    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("Disconnected!");
            break;
        case WStype_CONNECTED:
            {
                IPAddress ip = webSocket.remoteIP(num);
                Serial.print("Connected from ");
                Serial.println(ip);
        
        // send message to client
        webSocket.sendTXT(num, "Connected");
            }
            break;
        case WStype_TEXT:
            Serial.print("get Text: ");
            Serial.println(*payload);

            // send message to client
             webSocket.sendTXT(num, "message here");

            // send data to all connected clients
             webSocket.broadcastTXT("message here");
            break;
        case WStype_BIN:
            Serial.print("get binary length: ");
            Serial.println(lenght);
            hexdump(payload, lenght);

            // send message to client
            webSocket.sendBIN(num, payload, lenght);
            break;
    }
}


void setup() {
  // put your setup code here, to run once:
    Serial.begin(115200);

    Serial.println("VR Tracker by Jules Thuillier");
    
    pixy.init();
  


    //WiFiManager
    //Local intialization. Once its business is done, there is no need to keep it around
    WiFiManager wifiManager;
    //reset saved settings
 //   wifiManager.resetSettings();
    
    //fetches ssid and pass from eeprom and tries to connect
    //if it does not connect it starts an access point with the specified name
    //here  "AutoConnectAP"
    //and goes into a blocking loop awaiting configuration
    wifiManager.autoConnect("VR Tracker CAM", "julesthuillier");

    //if you get here you have connected to the WiFi
    Serial.println("Wifi connection established");

    ESPhttpUpdate.update("159.203.8.64", 80, "/vrtracker/vrtracker.bin");

    webSocket.begin();
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
          webSocket.sendTXT(0, data);
       // }
      }   
  }  
  
  else {
      delayMicroseconds(20);
  } 
  
}
