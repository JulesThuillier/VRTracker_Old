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
byte addresses[][6] = {"1Node","2Node"};              // Radio pipe addresses for the 2 nodes to communicate.

// Role management: Set up role.  This sketch uses the same software for all the nodes
// in this system.  Doing so greatly simplifies testing.  
typedef enum { role_ping_out = 1, role_pong_back } role_e;                 // The various roles supported by this sketch
const char* role_friendly_name[] = { "invalid", "Ping out", "Pong back"};  // The debug-friendly names of those roles
role_e role = role_pong_back;                                              // The role of the current running sketch

byte counter = 1;                                                          // A single byte to keep track of the data being sent back and forth


void setup(){

  Serial.begin(115200);
  Serial.println(F("RF24/examples/GettingStarted_CallResponse"));
  Serial.println(F("*** PRESS 'T' to begin transmitting to the other node"));
  //printf_begin();
  // Setup and configure radio
  
 // pinMode(pixy_SS,OUTPUT);
 // digitalWrite(pixy_SS, HIGH);

  radio.begin();

  radio.enableAckPayload();                     // Allow optional ack payloads
  radio.enableDynamicPayloads();                // Ack payloads are dynamic payloads
  radio.setPALevel(RF24_PA_MAX);
  radio.setDataRate(RF24_1MBPS);
  radio.setCRCLength(RF24_CRC_8);          // Use 8-bit CRC for performance
  
  if(radioNumber){
    radio.openWritingPipe(addresses[1]);        // Both radios listen on the same pipes by default, but opposite addresses
    radio.openReadingPipe(1,addresses[0]);      // Open a reading pipe on address 0, pipe 1
  }else{
    radio.openWritingPipe(addresses[0]);
    radio.openReadingPipe(1,addresses[1]);
  }
  radio.startListening();                       // Start listening  
  
  radio.writeAckPayload(1,&counter,1);          // Pre-load an ack-paylod into the FIFO buffer for pipe 1
  radio.printDetails();
}

void loop(void) {

  
/****************** Ping Out Role ***************************/

  if (role == role_ping_out){                               // Radio is in ping mode

    byte gotByte;                                           // Initialize a variable for the incoming response
    
    radio.stopListening();                                  // First, stop listening so we can talk.      
    Serial.print(F("Now sending "));                         // Use a simple byte counter as payload
    Serial.println(counter);
    
    unsigned long time = micros();                          // Record the current microsecond count   
                                                            
    if ( radio.write(&counter,1) ){                         // Send the counter variable to the other radio 
        if(!radio.available()){                             // If nothing in the buffer, we got an ack but it is blank
            Serial.print(F("Got blank response. round-trip delay: "));
            Serial.print(micros()-time);
            Serial.println(F(" microseconds"));     
        }else{      
            while(radio.available() ){                      // If an ack with payload was received
                radio.read( &gotByte, 1 );                  // Read it, and display the response time
                unsigned long timer = micros();
                
                Serial.print(F("Got response "));
                Serial.print(gotByte);
                Serial.print(F(" round-trip delay: "));
                Serial.print(timer-time);
                Serial.println(F(" microseconds"));
                counter++;                                  // Increment the counter variable
            }
        }
    
    }else{        Serial.println(F("Sending failed.")); }          // If no ack response, sending failed
    
    delay(20);  // Try again later
  }


/****************** Pong Back Role ***************************/

  if ( role == role_pong_back ) {
    byte pipeNo, gotByte;                          // Declare variables for the pipe and the byte received
    while( radio.available(&pipeNo)){              // Read all available payloads
      radio.read( &gotByte, 1 );                   
                                                   // Since this is a call-response. Respond directly with an ack payload.
      gotByte += 1;                                // Ack payloads are much more efficient than switching to transmit mode to respond to a call
      radio.writeAckPayload(pipeNo,&gotByte, 1 );  // This can be commented out to send empty payloads.
      Serial.print(F("Loaded next response"));
      Serial.println(gotByte);  
   }
 }



/****************** Change Roles via Serial Commands ***************************/

  if ( Serial.available() )
  {
    char c = toupper(Serial.read());
    if ( c == 'T' && role == role_pong_back ){      
      Serial.println(F("*** CHANGING TO TRANSMIT ROLE -- PRESS 'R' TO SWITCH BACK"));
      role = role_ping_out;  // Become the primary transmitter (ping out)
      counter = 1;
   }else
    if ( c == 'R' && role == role_ping_out ){
      Serial.println(F("*** CHANGING TO RECEIVE ROLE -- PRESS 'T' TO SWITCH BACK"));      
       role = role_pong_back; // Become the primary receiver (pong back)
       radio.startListening();
       counter = 1;
       radio.writeAckPayload(1,&counter,1);
       
    }
  }
}
