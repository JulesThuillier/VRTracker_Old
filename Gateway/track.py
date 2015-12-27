import cv2
import numpy as np
import time
import datetime
import sys
import OSC
import atexit
from threading import Thread
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

run = False
calibration_over = False

receive_address = '192.168.42.103', 8338

ip_rasp_1 = '192.168.42.75'
ip_rasp_2 = '192.168.42.129'

port = 8338
remote_ip = "192.168.42.131"
my_ip = "192.168.42.103"


client = OSC.OSCClient()
client.connect((remote_ip,port))

server = OSC.OSCServer(receive_address)
server.timeout = 0

rasp_1 = ""
rasp_2 = ""

rasp_1_point = [0.0, 0.0]
rasp_2_point = [0.0, 0.0]

projMat1 = None
projMat2 = None


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

################ CAMERA ################

#camera_matrix =  np.float64([[ 630.02180182, 0.0, 324.93277787], [0.0, 629.01122843, 234.7133668], [0.0, 0.0,1.0]])
#dist_coef = np.float64([0.04857147, -0.15865516, -0.00248904,  0.0017063,  -0.2206133 ])

camera_matrix_rasp_1 = np.float64([[ 404.8008372, 0., 305.5109283 ], [0., 404.63782086, 316.34525606], [0., 0., 1.]])
dist_coef_rasp_1 = np.float64([-0.37689891, 0.12999331, 0.01321258, -0.00388016, -0.02054299])

camera_matrix_rasp_2 = np.float64([[ 377.24187935, 0., 315.01426647],[0., 377.54906425, 259.7139808 ], [0., 0., 1.]])
dist_coef_rasp_2 = np.float64([-0.34371664, 0.10197198, 0.00315668, -0.00165892, -0.01461753])


#########################################

def update_position():
    res = np.zeros(3)

    myout = cv2.triangulatePoints(projMat1,projMat2, np.float32(rasp_1_point), np.float32(rasp_2_point))

    print myout
    print len(myout)

    mypoint1 = np.array([myout[0], myout[1], myout[2]])
    mypoint1 = mypoint1.reshape(-1, 3)
    mypoint1 = np.array([mypoint1])
    P_24x4 = np.resize(projMat1, (4,4))
    P_24x4[3,0] = 0
    P_24x4[3,1] = 0
    P_24x4[3,2] = 0
    P_24x4[3,3] = 1

    projected = cv2.perspectiveTransform(mypoint1, P_24x4)
    print projected

    output2 = myout[:-1]/myout[-1]
    print output2
    
    ax.scatter(output2[0], output2[1], -output2[2], 'r', 'o')
    plt.draw()



def update_coordinates(point, coordinates):
    global rasp_1_point
    global rasp_2_point
    
    xy_array = coordinates[0].split('-', 1 );
    print xy_array
    if(point == 1):
        rasp_1_point = [float(xy_array[0]), float(xy_array[1])]
    if(point == 2):
        rasp_2_point = [float(xy_array[0]), float(xy_array[1])]
    
    if(calibration_over == True):
        update_position()
    

def point_callback(addr, tags, stuff, source):
    
    global rasp_1
    global rasp_2
    if(source == rasp_1):
       # print("Raspb 1 reception")
        update_coordinates(1, stuff)
    
    elif(source == rasp_2):
      #  print("Raspb 2 reception")
        update_coordinates(2, stuff)
        
    # First time message is received
    # Check if IP is corresponding
    elif ip_rasp_1 in OSC.getUrlStr(source):
        print("First message received from : " + str(OSC.getUrlStr(source)))
        rasp_1 = source
        
    elif ip_rasp_2 in OSC.getUrlStr(source):
        print("First message received from : " + str(OSC.getUrlStr(source)))
        rasp_2 = source


# user script that's called by the game engine every frame
def each_frame(threadname):
    # clear timed_out flag
    server.timed_out = False
    # handle all pending requests then return
    while not server.timed_out:
        server.handle_request()

        


######################################################
###############      EXIT HANDLER      ###############
######################################################

def exit_handler():
    print 'My application is ending!'
    thread1.join()
    server.close()
atexit.register(exit_handler)


#############################################
################## START ####################
#############################################

server.addMsgHandler( "/point/0", point_callback )
server.addMsgHandler( "/point/1", point_callback )
server.addMsgHandler( "/point/2", point_callback )

print("Server is starting on " + str(receive_address))

thread1 = Thread( target=each_frame, args=("1") )
thread1.start()

#############################################
########### CALIBRATION SEQUENCE ############
#############################################


print "\n\nWe are about to calibrate the cameras\n"
print "Calibration steps : "
print "2 --------- 3\n|           |\n|           |\nb           |\n|           |\n|           |\n1 ----a---- 4"
print"\n Go to point 1"
raw_input("When arrived, press Enter")
coin_1_rasp_1 = rasp_1_point
coin_1_rasp_2 = rasp_2_point

address = "/distortionNoLens/"
msg = OSC.OSCMessage()
msg.setAddress(address)
client.send(msg)

print"\n Go to point 2"
raw_input("When arrived, press Enter")
coin_2_rasp_1 = rasp_1_point
coin_2_rasp_2 = rasp_2_point

address = "/matrixLens/"
msg = OSC.OSCMessage()
msg.setAddress(address)
client.send(msg)


print"\n Go to point 3"
raw_input("When arrived, press Enter")
coin_3_rasp_1 = rasp_1_point
coin_3_rasp_2 = rasp_2_point


address = "/matrixNoLens/"
msg = OSC.OSCMessage()
msg.setAddress(address)
client.send(msg)


print"\n Go to point 4"
raw_input("When arrived, press Enter")
coin_4_rasp_1 = rasp_1_point
coin_4_rasp_2 = rasp_2_point


address = "/distortionLens/"
msg = OSC.OSCMessage()
msg.setAddress(address)
client.send(msg)



# Calibration square in camera coordinates
calibration_square_rasp1 = np.float32([coin_1_rasp_1, coin_2_rasp_1, coin_3_rasp_1, coin_4_rasp_1])
calibration_square_rasp2 = np.float32([coin_1_rasp_2, coin_2_rasp_2, coin_3_rasp_2, coin_4_rasp_2])

print"\n Camera 1 calibration square : "
print calibration_square_rasp1
print"\n Camera 2 calibration square : "
print calibration_square_rasp2

a = input("\n Enter length a in cm : ")
b = input("\n Enter length b in cm : ")
user_height = input("\n Enter your height in cm : ")




#############################################
########## CALIBRATION CALCULATION ##########
#############################################


# Calibration square in world coordinates
square_tag_coordinates = np.float32([[0, 0, user_height], [0, a, user_height], [b, a, user_height], [b, 0, user_height]])

######## CAMERA 1 ########

ret1, rvec1, tvec1 = cv2.solvePnP(square_tag_coordinates, calibration_square_rasp1, camera_matrix_rasp_1, dist_coef_rasp_1)	
rotM_cam = cv2.Rodrigues(rvec1)[0]

# calculate camera position (= translation), in mm from 0,0,0 point
camera1Position = -np.matrix(rotM_cam).T * np.matrix(tvec1)
print "Camera 1 position :"
print camera1Position

camMatrix1 = np.append(cv2.Rodrigues(rvec1)[0], tvec1, 1)

print "Camera 1 matrix :"
print camMatrix1

projMat1 = np.dot(camera_matrix_rasp_1, camMatrix1)

print "Projection matrix 1 :"
print projMat1

######## CAMERA 2 ########

ret2, rvec2, tvec2 = cv2.solvePnP(square_tag_coordinates, calibration_square_rasp2, camera_matrix_rasp_2, dist_coef_rasp_2)
rotM_cam2 = cv2.Rodrigues(rvec2)[0]

# calculate camera position (= translation), in mm from 0,0,0 point
cameraPosition2 = -np.matrix(rotM_cam2).T * np.matrix(tvec2)
print "Camera 2 position :"
print cameraPosition2

camMatrix2 = np.append(cv2.Rodrigues(rvec2)[0], tvec2, 1)

print "Camera 2 matrix :"
print camMatrix2

projMat2 = np.dot(camera_matrix_rasp_2, camMatrix2)

print "Projection matrix 2 :"
print projMat2


print "\n CALIBRATION IS OVER !"
calibration_over = True


#############################################
################## 3D PLOT ##################
#############################################

ax.legend()

ax.set_xlim3d(-b, b*2)
ax.set_ylim3d(-a, a*2)
ax.set_zlim3d(0, 250)

ax.scatter(12, 150, 80,s=20, c=u'b', marker=u'o')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()


################  LOOP ################

# simulate a "game engine"
while True:
    # do the game stuff:
    time.sleep(1)
    # call user script
   # each_frame()

thread1.join()
server.close()