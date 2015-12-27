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

global clients

def new_client(client, server):
    print 'New client has joined'
    global clients
    clients = client
    print clients

def message_from_client(client, server, message):
    print 'Message received from ', client, ' : ', message

server = WebsocketServer(9019, "192.168.1.101")
server.set_fn_new_client(new_client)
server.set_fn_message_received(message_from_client)


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
radio.printDetails()

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

proj_matrix = None  # Contains projection matrix for each cameras (calculated at calibration)
XY_points = None  # Contains the last 2D points for each camera (or arrays of 2D points if a camera detects more than 1 point)


#############################################
#################      MAIN       ###################
#############################################

XY_Queue = Queue(maxsize=10)
XYZ_Queue = Queue(maxsize=10)

def websocket_thread():
    server.run_forever()
    
def websocket_send_thread():
    while True:
        if not XYZ_Queue.empty():
            worker = XYZ_Queue.get()
            server.send_message(clients, worker)
            XYZ_Queue.task_done()

def rf24_receive_thread():
    while True:
        if not XY_Queue.full():
                pipeNumber = radio.available_pipe()
                if pipeNumber[0]:
                    receive_payload = radio.read(3)
                    XY_Queue.put( receive_payload)
                    print 'pipe number = ', pipeNumber[0], ' - ', pipeNumber[1] 
        else :
            print 'XY Queue is full'


def calculate_XYZ_thread():
    while True:
	valuetosend = 0
        if not XY_Queue.empty():
                valuetosend = XY_Queue.get()
                # CALCULATE 3D POSITION HERE
                XY_Queue.task_done()
        if not XYZ_Queue.full():
                if valuetosend != 0:
                    print valuetosend
                    XYZ_Queue.put(valuetosend)
        else :
            print 'XYZ Queue is full'

websocket_running_th = Thread( target=websocket_thread)
websocket_send_th =  Thread( target=websocket_send_thread)
rf24_receiver_th =  Thread( target=rf24_receive_thread)
calculate_3D_th =  Thread( target=calculate_XYZ_thread)

websocket_running_th.deamon = True
websocket_send_th.deamon =  True
rf24_receiver_th.deamon =  True
calculate_3D_th.deamon = True

######################################################
###############      EXIT HANDLER      ###############
######################################################

def exit_handler():
    print 'My application is ending!'
    websocket_running_th.join()
    websocket_send_th.join()
    rf24_receiver_th.join()
    calculate_3D_th.join()
    server.close()
atexit.register(exit_handler)

websocket_running_th.start()
websocket_send_th.start()
rf24_receiver_th.start()
calculate_3D_th.start()

