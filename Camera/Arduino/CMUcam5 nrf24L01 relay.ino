//
// begin license header
//
// This file is part of Pixy CMUcam5 or "Pixy" for short
//
// All Pixy source code is provided under the terms of the
// GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
// Those wishing to use Pixy source code, software and/or
// technologies under different licensing terms should contact us at
// cmucam@cs.cmu.edu. Such licensing terms are available for
// all portions of the Pixy codebase presented here.
//
// end license header
//

/* 
   06.04.2014 v0.1.3 John Leimon
     + Now using pixy.init() to initialize Pixy in setup().
*/

#include <SPI.h>  
#include <Pixy.h>
#include "RF24.h"
#include "PixyUART.h"

Pixy pixy;

/****************** User Config ***************************/
/***      Set this radio as radio number 0 or 1         ***/
bool radioNumber = 0;

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 7 & 8 */
RF24 radio(7,8);
/**********************************************************/

// Les addresses de communication sans fil
byte addresses[][6] = {"Came1","Base1"};

// Used to control whether this node is sending or receiving
bool role = 1;
unsigned long time = 0;

unsigned int led1 = 5;

uint16_t * datas = new uint16_t[5];

void setup()
{

  Serial.begin(19200);
  Serial.print("Starting...\n");

  pixy.init();
  
  pinMode(led1, OUTPUT);

  radio.begin();                           // Setup and configure rf radio
//  radio.setChannel(1);
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setAutoAck(0);                     // Ensure autoACK is disabled
//  radio.setRetries(2,15);                  // Optionally, increase the delay between retries & # of retries
  
 // radio.setCRCLength(RF24_CRC_8);          // Use 8-bit CRC for performance
  //radio.openWritingPipe(pipes[0]);
  //radio.openReadingPipe(1,pipes[1]);
  
  // Open a writing and reading pipe on each radio, with opposite addresses
if(radioNumber){
    radio.openWritingPipe(addresses[1]);
    radio.openReadingPipe(1,addresses[0]);
  }else{
    radio.openWritingPipe(addresses[0]);
    radio.openReadingPipe(1,addresses[1]);
  }
  
  radio.stopListening();
  radio.powerUp();       
     
}

void loop()
{ 
  uint16_t blocks;
  blocks = pixy.getBlocks();
  
  if (blocks)
  { 
    
    if (true)
    {

      for (int j=0; j<blocks; j++)
      {
        datas[0]=pixy.blocks[j].signature;
        datas[1]=pixy.blocks[j].x;
        datas[2]=pixy.blocks[j].y;
        datas[3]=pixy.blocks[j].width;
        datas[4]=pixy.blocks[j].height;
 
      //  pixy.blocks[j].print();

        bool ans = radio.writeFast(datas, sizeof(uint16_t)*5);
        if(ans) {
         digitalWrite(led1, HIGH);
        }
        Serial.println("Sent... "+ ans);
      }
    }
    
  }  
  else {
      digitalWrite(led1, LOW); 
      delayMicroseconds(50);
  }
}

