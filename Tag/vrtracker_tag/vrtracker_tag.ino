#include <ESP8266httpUpdate.h> // For Server OTA
#include <ESP8266WiFi.h>          //https://github.com/esp8266/Arduino

//needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>         //https://github.com/tzapu/WiFiManager
#include <WebSocketsClient.h>

WebSocketsClient webSocket;

const int led_Red_pin = 0;
const int led_Green_pin = 4;
const int led_Blue_pin = 5;
const int led_Ir_pin = 12;
const int led_Ir_pin_2 = 16;
const int battery_Reading = A0;

boolean maxPower = false;

String macadress = ""; 
IPAddress ip;
String strIP;

// Turn the IR light OFF
void light_off(){
  digitalWrite(led_Ir_pin, LOW); 
  digitalWrite(led_Ir_pin_2, LOW); 
}

// Turn the IR light OFF wait for "timeMS" and turn it back ON (ping)
void light_offon(uint16_t timeMS){
  digitalWrite(led_Ir_pin, LOW);
  digitalWrite(led_Ir_pin_2, LOW);
  delay(timeMS);
  digitalWrite(led_Ir_pin, HIGH);
  if(maxPower){
    digitalWrite(led_Ir_pin_2, HIGH); 
  }  
}

// Turn the IR light ON
void light_on(boolean power){
  Serial.println("IR On");
  maxPower = power;
  digitalWrite(led_Ir_pin, HIGH); 
  if(maxPower){
    digitalWrite(led_Ir_pin_2, HIGH); 
  }
  
}

// Set RGB Led color
void rgb(uint16_t r, uint16_t g, uint16_t b){
  analogWrite(led_Red_pin, 1023-r);
  analogWrite(led_Green_pin, 1023-g);
  analogWrite(led_Blue_pin, 1023-b);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t lenght) {

    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[WSc] Disconnected!\n");
            light_off();
            break;
        case WStype_CONNECTED:
            {
                Serial.printf("[WSc] Connected to url: %s\n",  payload);
                webSocket.sendTXT("tag-"+macadress);
            }
            break;
        case WStype_TEXT:
          {
            Serial.printf("[WSc] get text: %s\n", payload);
            String command = (char*)payload;
            Serial.println("Command Received : " + command);
            
            if(command.startsWith("on:")){
              String strValue=command.substring(3);
              bool value = false;
              if(strValue == "1"){
                value = true;
              }
              light_on(value);
            }
            else if(command == "off"){
              light_off();
            }
            else if(command.startsWith("offon:")){
              String strValue=command.substring(6);
              int value = strValue.toInt();
              Serial.println(value);
              light_offon(value);
            }
            else if(command.startsWith("rgb:")){
              String strValue= command.substring(4);
              int index = strValue.indexOf('-');
              String strR = strValue.substring(0, index);
              strValue = strValue.substring(index+1);
              index = strValue.indexOf('-');
              String strG = strValue.substring(0, index);
              strValue = strValue.substring(index+1);
              index = strValue.indexOf('-');
              String strB = strValue.substring(0, index);
              int r = strR.toInt();
              int g = strG.toInt();
              int b = strB.toInt();
              rgb(r,g,b);
            }
          }
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
    pinMode(led_Ir_pin_2, OUTPUT);
    pinMode(battery_Reading, INPUT);

    rgb(400,400,400);
    light_off();
    
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
    wifiManager.autoConnect("VR Tracker TAG", "vrtracker");
    Serial.println("Wifi connection established");

    /*char* buffer;
    ip = WiFi.localIP();
    sprintf(buffer,"%d:%d:%d:%d", ip[0],ip[1],ip[2],ip[3]);*/
    
    strIP = WiFi.gatewayIP().toString();
    Serial.println("My IP : " + WiFi.localIP().toString());
    Serial.println("Gateway IP : " + strIP);

    // Check for software update
    ESPhttpUpdate.update("http://www.julesthuillier.com/vrtracker/arduino/tag.bin");

   
    // Start websocket client
    if(strIP == "192.168.10.1"){
      webSocket.begin(strIP, 8001);
    }
    else{
      webSocket.begin("192.168.1.113", 8001);
    }
    
    webSocket.onEvent(webSocketEvent);  
}

void loop() {
  webSocket.loop();
}
