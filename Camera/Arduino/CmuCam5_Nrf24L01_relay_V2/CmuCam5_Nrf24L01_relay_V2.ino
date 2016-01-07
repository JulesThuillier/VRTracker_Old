/******* Below are the mandotory licenses header for the libraries, please don't remove them 
* Dec 2015 - Jules Thuillier
* thuillierjules@gmail.com
* 
* Description :
* This program sends positions data from a CmuCam5 tracking camera 
* over the air using a Nrf24L01+ wireless chip.
* Please check out this website for more informations :
* http://julesthuillier.com/virtual-reality-diy-position-tracking-system-introduction/
*
************************************************************************/
/*
* begin license header
*
* This file is part of Pixy CMUcam5 or "Pixy" for short
*
* All Pixy source code is provided under the terms of the
* GNU General Public License v2 (http://www.gnu.org/licenses/gpl-2.0.html).
* Those wishing to use Pixy source code, software and/or
* technologies under different licensing terms should contact us at
* cmucam@cs.cmu.edu. Such licensing terms are available for
* all portions of the Pixy codebase presented here.
*
* end license header
******************************************************************/
 
#include <SPI.h>
//#include <Pixy.h>
#include "PixySPI_SS.h"
#include "RF24.h"

#define pixy_SS  10  //the Slave Select pin that pixy is on

PixySPI_SS pixy(pixy_SS);

/****************** User Config ***************************/
/***      Set this radio as radio number 0 or 1         ***/
bool radioNumber = 0;

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 7 & 8 */
RF24 radio(7,8);
/**********************************************************/
                                                                           // Topology
const uint64_t addresses[6] = {0xF0F0F0F0F1LL, 0xF0F0F0F0E2LL, 0xF0F0F0F0D3LL, 0xF0F0F0F0C4LL, 0xF0F0F0F0B5LL, 0xF0F0F0F0A6LL};              // Radio pipe addresses for the 2 nodes to communicate.

int address = 2;                                              // The role of the current running sketch
uint16_t blocks;
uint16_t old_blocks;

void setup(){

  Serial.begin(115200);
//  Serial.println(F("RF24/examples/GettingStarted_CallResponse"));
//  Serial.println(F("*** PRESS 'T' to begin transmitting to the other node"));
  //printf_begin();
  // Setup and configure radio
  
  pinMode(pixy_SS,OUTPUT);
 // digitalWrite(pixy_SS, HIGH);
  pixy.init();

  radio.begin();

  radio.enableAckPayload();                     // Allow optional ack payloads
  radio.enableDynamicPayloads();                // Ack payloads are dynamic payloads
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setCRCLength(RF24_CRC_8);          // Use 8-bit CRC for performance
 // radio.setPayloadSize(4);
  radio.openWritingPipe(addresses[address]);        // Both radios listen on the same pipes by default, but opposite addresses
  radio.openReadingPipe(1,addresses[0]);      // Open a reading pipe on address 0, pipe 1

  
  radio.powerUp();   
 // radio.startListening();                       // Start listening  
  radio.stopListening();                                  // First, stop listening so we can talk.      
  
//  radio.writeAckPayload(1,&counter,1);          // Pre-load an ack-paylod into the FIFO buffer for pipe 1
  radio.printDetails();
}

void loop(void) {
    
  old_blocks = blocks;
  blocks = pixy.getBlocks();
  
  if (blocks && (old_blocks != blocks))
  { 
    if (true)
    {

      for (int j=0; j<blocks; j++)
      {
        if(pixy.blocks[j].width < 30 && pixy.blocks[j].height < 30){
          uint32_t datas = 0;
          uint32_t x, y, sig = 0;
          y = 0x00000FFF & pixy.blocks[j].y;
          x = pixy.blocks[j].x & 0x0FFF;
          sig = j;//pixy.blocks[j].signature & 0x000F;
          for (byte i=0; i<12; i++) {
                 x = x<<1;
          }
          for (byte i=0; i<24; i++) {
                 sig = sig<<1;
          }
          datas = y | x | sig;
          digitalWrite(pixy_SS, HIGH);
        //  Serial.println(sig);
        //  Serial.println(x);
          bool ans = radio.write(&datas, sizeof(datas));
          if(ans) {
  
          }  
          digitalWrite(pixy_SS, LOW);  
          delayMicroseconds(20);
        }
      }
    }    
  }  
  
  else {
      delayMicroseconds(20);
  }
}
