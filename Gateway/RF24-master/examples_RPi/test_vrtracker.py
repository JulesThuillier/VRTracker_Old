#!/usr/bin/env python

#
# Example using Dynamic Payloads
# 
#  This is an example of how to use payloads of a varying (dynamic) size.
# 

import time
from RF24 import *


########### USER CONFIGURATION ###########
# See https://github.com/TMRh20/RF24/blob/master/RPi/pyRF24/readme.md

# CE Pin, CSN Pin, SPI Speed

# Setup for GPIO 22 CE and GPIO 25 CSN with SPI Speed @ 1Mhz
#radio = RF24(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_18, BCM2835_SPI_SPEED_1MHZ)

# Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 4Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_4MHZ)

#RPi B
# Setup for GPIO 15 CE and CE1 CSN with SPI Speed @ 8Mhz
#radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

#RPi B+
# Setup for GPIO 22 CE and CE0 CSN for RPi B+ with SPI Speed @ 8Mhz
radio = RF24(RPI_BPLUS_GPIO_J8_22, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)

##########################################

pipes = [0xF0F0F0F0F1, 0xF0F0F0F0E2, 0xF0F0F0F0D3, 0xF0F0F0F0C4, 0xF0F0F0F0B5, 0xF0F0F0F0A6]
millis = lambda: int(round(time.time() * 1000))

print 'Starting VrTracker...'

radio.begin()
radio.setRetries(5,15)
radio.printDetails()

print ' ************ Role Setup *********** '

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1]);
radio.openReadingPipe(2, pipes[2]);
radio.openReadingPipe(3, pipes[3]);
radio.openReadingPipe(4, pipes[4]);
radio.openReadingPipe(5, pipes[5]);
radio.startListening();

# forever loop
while 1:
   
    # if there is data ready
    pipeNumber = radio.available()
    if pipeNumber:
        while radio.available():
            receive_payload = radio.read(3)

            # Spew it
            print 'Got payload, value="', receive_payload, '"'

            # Calculate 3D position here
