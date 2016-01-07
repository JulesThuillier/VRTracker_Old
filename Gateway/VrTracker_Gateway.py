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
import os.path

#############################################
################  WEBSOCKETS  #################
#############################################

global clients
clients = []
global cameras_xy # Contains last XY points for each camera
cameras_xy = np.zeros(shape=(6,2))
global calibration
calibration = False
global detectingCameras
detectingCameras = False
max_cameras = 6
global calibPoints
calibPoints = np.zeros((max_cameras,20,2), dtype=np.float32)
global worldCoordinates
worldCoordinates = np.array([], dtype=np.float32).reshape(0,3)
global cameras_index
cameras_index =[1,2]
global projectionMatrix
projectionMatrix = np.array([], dtype=np.float32).reshape(0,3,4)
global tracking
tracking = False


server = WebsocketServer(9014, "192.168.1.101")

global camera_matrix
camera_matrix = np.float64([[247.9139798, 0., 155.30251177], [0., 248.19822494, 100.74688813], [0.,  0., 1.]])
global dist_coef
dist_coef = np.float64([-0.45977769,  0.29782977, -0.00162724,  0.00046035, -0.16351777])


def startCalibration():
    calibration = True
    global calibPoints
    global cameras_index
    calibPoints = np.zeros((len(cameras_index),20,2), dtype=np.float32)

def addCalibrationPoint(message):
    # Get XYZ reel space coordinates from websocket 
    message = message.split(':')[1]
    xyz = message.split('-')
    global worldCoordinates 
    global calibPoints
    global cameras_index
    worldCoordinates = np.append(worldCoordinates, [xyz], axis=0) # Add 3D point to World Coordinates
    print "World Coordinates : "
    print worldCoordinates
    numberOfPoints = worldCoordinates.shape
    print "Point Index : "
    print numberOfPoints[0]
    print "Camera XY : "
    print cameras_xy
    print "Calib Points : "
    

    # Add the new point for each camera
    for i in range(len(cameras_index)):
	calibPoints[i, (numberOfPoints[0])-1, 0] = float(cameras_xy[cameras_index[i]][0])
	calibPoints[i, (numberOfPoints[0])-1, 1] = float(cameras_xy[cameras_index[i]][1])

    print calibPoints

def endCalibration():
    calibration = False
    global calibPoints
    global cameras_index
    
    # Calculate and save projection matrix here
    calculateProjectionMatrix(worldCoordinates, calibPoints)
    calibPoints = np.zeros((len(cameras_index),20,2))

def calculateProjectionMatrix(world, camera):

    global projectionMatrix
    projectionMatrix = np.array([], dtype=np.float32).reshape(0,3,4)
    for i in range(len(cameras_index)):
	points = camera[i, 0:(worldCoordinates.shape)[0], 0:2]
	point = np.float32(points)
	myworld = np.float32(world)
	print "Camera " + str(i) + " points : "
	print point
	print "World : "
	print myworld
	print "dist_coef : "
	print dist_coef
	print "camera_matrix : "
	print camera_matrix

	ret, rvec, tvec = cv2.solvePnP(myworld, point, camera_matrix, dist_coef)	
	rotM_cam = cv2.Rodrigues(rvec)[0]

# calculate camera position (= translation), in mm from 0,0,0 point
	cameraPosition = -np.matrix(rotM_cam).T * np.matrix(tvec)
	print "Camera " + str(i) + " position : "
	print cameraPosition

	camMatrix = np.append(cv2.Rodrigues(rvec)[0], tvec, 1)
	projMat = np.dot(camera_matrix, camMatrix)

	projectionMatrix = np.append(projectionMatrix, [projMat], axis=0)
    saveProjectionMatrix(projectionMatrix)

def loadProjectionMatrix():
    filename = "projetionmatrix"
    global projectionMatrix
    if os.path.isfile(filename+'.npy'):
	print "Projection Matrix Loaded"
	projectionMatrix = np.load(filename+'.npy')
    return projectionMatrix


def saveProjectionMatrix(projectionMatrix):
    filename = "projetionmatrix"
    if os.path.isfile(filename):
	os.remove(filename)
    np.save(filename, projectionMatrix) 

def detectCamera(index):
    global cameras_index
    if not index in cameras_index:
        cameras_index.append(index)

def new_client(client, server):
    print 'New client has joined'
    global clients
    clients.append(client)
    print clients

def calculate3D():
    global projectionMatrix
    global cameras_xy
    global cameras_index
    myout = cv2.triangulatePoints(projectionMatrix[0],projectionMatrix[1], np.float32(cameras_xy[cameras_index[0]]), np.float32(cameras_xy[cameras_index[1]]))

    mypoint1 = np.array([myout[0], myout[1], myout[2]])
    mypoint1 = mypoint1.reshape(-1, 3)
    mypoint1 = np.array([mypoint1])
    P_24x4 = np.resize(projectionMatrix[0], (4,4))
    P_24x4[3,0] = 0
    P_24x4[3,1] = 0
    P_24x4[3,2] = 0
    P_24x4[3,3] = 1

    projected = cv2.perspectiveTransform(mypoint1, P_24x4)
    output2 = myout[:-1]/myout[-1]
    print output2
    return output2


def startTracking():
    global tracking
    tracking = True

def message_from_client(client, server, message):
    print 'Message received from ', client, ' : ', message
    global detectingCameras

    if message == "calibrate":
        print 'Start Calibration'
        calibration = True

    elif message == "ok":
        print 'Start Calibration'

    elif message.startswith("xyz:"):
        addCalibrationPoint(message)

    elif message == "end":
        print 'End'
        endCalibration()

    elif message == "end calibration":
        print 'End Calibration'
        endCalibration()      

    elif message == "end detection":
        print 'Stop detecting cameras'
        detectingCameras = False
	print str(len(cameras_index)) + " cameras found"

    elif message == "detect":
        print 'Detecting cameras'
        detectingCameras = True

    elif message == "exit":
        print 'Stop server'
	server.stop()

    elif message == "start":
        print 'Start tracking'
	startTracking()

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


proj_matrix = None  # Contains projection matrix for each cameras (calculated at calibration)
XY_points = None  # Contains the last 2D points for each camera (or arrays of 2D points if a camera detects more than 1 point)

loadProjectionMatrix()
print projectionMatrix


#############################################
#################      MAIN       ###################
#############################################

XY_Queue = Queue(maxsize=100)
XYZ_Queue = Queue(maxsize=100)

def parse(pipe, value):
    y =((ord(value[1]) & 0x0F) << 8) | (ord(value[0]))
    x = (((ord(value[2]) << 4) & 0x0FF0) | (0x0F & (ord(value[1]) >> 4)) ) & 0x0FFF
    sig = ord(value[3])
    parsed_value = [pipe, sig, x, y]
    return parsed_value

def websocket_thread():
    server.run_forever()
    
def websocket_send_thread():
    while True:
        if not XYZ_Queue.empty():
            worker = XYZ_Queue.get()
	    XYZ_Queue.task_done()
	    #if(len(worker)==3):
	       # val = str(worker[0]+ "|"+ worker[1] + "|" + worker[3]) #" ".join(str(e) for e in worker)
            server.send_message(clients[0], worker)
            

def rf24_receive_thread():
    while True:
        pipeNumber = radio.available_pipe()
        if pipeNumber[0]:
            len = radio.getDynamicPayloadSize()
            receive_payload = radio.read(len)
            value = [pipeNumber[1], receive_payload]    
	    if XY_Queue.full():    
             	XY_Queue.get()
		XY_Queue.task_done()
            XY_Queue.put(value)
	time.sleep(0.001)

def calculate_XYZ_thread():
    while True:
	valuetosend = None
	position = None
        if not XY_Queue.empty():
                valuetosend = XY_Queue.get()
		XY_Queue.task_done()
                # CALCULATE 3D POSITION HERE
                parsed_value = parse(valuetosend[0], valuetosend[1])
                cameras_xy[valuetosend[0]] = [parsed_value[2], parsed_value[3]]
		
                global detectingCameras
                if detectingCameras : 
		    print str(valuetosend[0]) + " : " + str(parsed_value)
                    detectCamera(valuetosend[0])

		global tracking
		if tracking:
			print "Tracking"
			position = calculate3D()
			position = str(position[0][0]) + "|" + str(position[1][0]) + "|" + str(position[2][0]) 
			print position	
                
        if not XYZ_Queue.full():
                if position != None:
                    print valuetosend
                    XYZ_Queue.put(position)
        else :
            print 'XYZ Queue is full'
	    time.sleep(0.02)

#websocket_running_th = Thread( target=websocket_thread)
websocket_send_th =  Thread( target=websocket_send_thread)
rf24_receiver_th =  Thread( target=rf24_receive_thread)
calculate_3D_th =  Thread( target=calculate_XYZ_thread)

#websocket_running_th.deamon = True
websocket_send_th.deamon =  True
rf24_receiver_th.deamon =  True
calculate_3D_th.deamon = True



######################################################
###############      EXIT HANDLER      ###############
######################################################

def exit_handler():
    print 'My application is ending!'
    #websocket_running_th.join()
    websocket_send_th.join()
    rf24_receiver_th.join()
    calculate_3D_th.join()
    server.close()
atexit.register(exit_handler)

#websocket_running_th.start()
websocket_send_th.start()
rf24_receiver_th.start()
calculate_3D_th.start()

server.run_forever()
print 'Ending'
#XYZ_Queue.join()
#XY_Queue.join()
print 'Queue joined'
websocket_send_th.join()
rf24_receiver_th.join()
calculate_3D_th.join()
sys.exit()
