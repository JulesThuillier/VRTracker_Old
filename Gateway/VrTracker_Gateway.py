#!/usr/bin/env python

import cv2
import numpy as np
import time
import datetime
import sys
import atexit
from Queue import Queue
from threading import Thread
from websocket_server import *
from RF24 import *

#############################################
################  WEBSOCKETS  #################
#############################################

def new_client(client, server):
    print 'New client has joined'

def message_from_client(client, server, message):
    print 'Message received from ', client, ' : ', message

server = WebsocketServer(62457)
server.set_fn_new_client(new_client)
server.set_fn_message_received(message_from_client)
server.run_forever()


#############################################
#################  RF24 radio  ###################
#############################################

radio = RF24(RPI_V2_GPIO_P1_15, RPI_BPLUS_GPIO_J8_24, BCM2835_SPI_SPEED_8MHZ)	
pipes = [0xF0F0F0F0F1, 0xF0F0F0F0E2, 0xF0F0F0F0D3, 0xF0F0F0F0C4, 0xF0F0F0F0B5, 0xF0F0F0F0A6]

radio.begin()
radio.setAutoAck(True)
radio.enableAckPayload()             # Allow optional ack payloads
radio.enableDynamicPayloads()        # Ack payloads are dynamic payloads
radio.setPALevel(RF24_PA_MAX)
radio.setDataRate(RF24_1MBPS)
radio.setCRCLength(RF24_CRC_8)       # Use 8-bit CRC for performance
radio.setRetries(5,15)
#radio.printDetails()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1]);
radio.openReadingPipe(2, pipes[2]);
radio.openReadingPipe(3, pipes[3]);
radio.openReadingPipe(4, pipes[4]);
radio.openReadingPipe(5, pipes[5]);
radio.startListening();


#############################################
#################   OPEN CV   ###################
#############################################

camera_matrix= np.float64([[ 404.8008372, 0., 305.5109283 ], [0., 404.63782086, 316.34525606], [0., 0., 1.]])
dist_coef = np.float64([-0.37689891, 0.12999331, 0.01321258, -0.00388016, -0.02054299])

proj_matrix[] = None  # Contains projection matrix for each cameras (calculated at calibration)
2D_points[] = None  # Contains the last 2D points for each camera (or arrays of 2D points if a camera detects more than 1 point)

######################################################
####################      EXIT HANDLER      ###################
######################################################

def exit_handler():
    print 'My application is ending!'
    thread1.join()
    server.close()
atexit.register(exit_handler)









