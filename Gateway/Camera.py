#!/usr/bin/env python
import numpy as np
from parse import *
import compute
import os.path
from Point2D import Point2D
from utils.Observer import Observable


class Camera:

    MAX_DISTANCE_BETWEEN_POINTS = 25
    MAX_SIZE_DIFF_BETWEEN_POINTS = 10


    def __init__(self, client, mac):
        self.client = client
        self.macadress = mac
        self.points2D = []
        self.new2DPointNotifier = Camera.New2DPointNotifier(self)
        self.point2DdeletedNotifier= Camera.Point2DdeletedNotifier(self)

        self.camera_matrix = np.float64([[247.9139798, 0., 155.30251177], [0., 248.19822494, 100.74688813], [0.,  0., 1.]])
        self.distortion_coefficient = np.float64([-0.45977769,  0.29782977, -0.00162724,  0.00046035, -0.16351777])
        self.projection_matrix = np.array([], dtype=np.float32).reshape(0,3,4)
        self.listOf2D3DPairCalibration = []
        self.calibrated = False
        self.calibrating = False

        self.loadCameraPreferences()


    def parsePointMessage(self, data):
        '''
        Parse data from Camera's  websocket to a dictionnay
        containing {'x': x, 'y': y, 'height': height, 'width': width};
        :param data: Raw String of this format '{id}x{x}y{y}h{h}w{w}a{a}'
        :return: Dictionnary if parsing succesfull
        '''
        extracted_data = parse("{id}x{x}y{y}h{h}w{w}a{a}", data)
        if len(extracted_data.named) == 6:
            return extracted_data.named
        else :
            return None

    def push(self, message):

        if self.calibrated != True and self.calibrating != True:
            print "Calibrate Camera First !"
            return
        parsedPoint = self.parsePointMessage(message)
        if(parsedPoint != None):
            self.addPoint(parsedPoint['x'], parsedPoint['y'], parsedPoint['h'], parsedPoint['w'])

    # Checks if points are lost
    def update(self):
        for point in self.points2D:
            if point.isLost():
                self.points2D.remove(point)
                self.point2DdeletedNotifier.notifyObservers()



    # Track if the new point received correspond to a point already recorded (to follow the point)
    # Argument is the point data in an array outputed by "parse" function
    def addPoint(self, x, y, height, width):
        updated = False
        for point in self.points2D:
            if point.distance(x, y) < self.MAX_DISTANCE_BETWEEN_POINTS*self.MAX_DISTANCE_BETWEEN_POINTS and point.sizeDifference(height, width) < self.MAX_SIZE_DIFF_BETWEEN_POINTS*self.MAX_SIZE_DIFF_BETWEEN_POINTS :

                # Notify as new point if it is still unassigned
                if(point.point3Dassigned == None):
                    self.new2DPointNotifier.notifyObservers()
                else:
                    point.update(x, y, height, width)
                updated = True
            else:
                point.count()
                # Remove lost points
                if point.isLost():
                    print '------------ Lost --------------'
                    self.points2D.remove(point)
                    self.point2DdeletedNotifier.notifyObservers()
        # Point not found, add it to the list and notify creation :
        if updated==False:
            print("CAMERA : NEW 2D Point  - " + str(x) + " - " + str(y))
            print self.points2D
            newPoint = Point2D(x, y, height, width, self)
            self.points2D.append(newPoint)
            self.new2DPointNotifier.notifyObservers()


    def enterCalibrationMode(self):
        self.listOf2D3DPairCalibration = []
        self.points2D = [] # Clean all 2D Points
        self.calibrating = True

    def exitCalibrationMode(self):
        print self.client['id']
        self.projection_matrix = np.array([], dtype=np.float32).reshape(0,3,4)
        points2DCalibration = np.array([], dtype=np.float32).reshape(0,2)
        world3DPoints = np.array([], dtype=np.float32).reshape(0,3)
        print self.listOf2D3DPairCalibration

        for pair in self.listOf2D3DPairCalibration:
            world3DPoints = np.append(world3DPoints, [pair[0]], axis=0)
            points2DCalibration = np.append(points2DCalibration, [pair[1]], axis=0)

        self.projection_matrix, position = compute.calculateProjectionMatrix(self, points2DCalibration, world3DPoints)
        self.saveCameraPreferences()
        self.calibrated = True
        self.calibrating = False
        return position


    def prepToRecordCalibrationPoint2D(self):
        self.points2D = []

    def saveCalibrationPoint2D(self, xyz):
        '''
        Save current 2D Point XY into an array to later
        associate this 2D array to 3D world coordinates
        to calibrate the camera and get projection matrix
        :return:
        '''
        if(len(self.points2D)>0):
            xy = [self.points2D[-1].buffer[-1]['x'], self.points2D[-1].buffer[-1]['y']]
            for pair in self.listOf2D3DPairCalibration:
                if pair[0] == xyz:
                    print "replacing pair"
                    pair[1] = xy
                    self.points2D = [] # Clean all 2D Points
                    return xy
            # If the XYZ point is not already recorded, add it to list
            self.listOf2D3DPairCalibration.append([xyz, xy])
            return xy

    def loadCameraPreferences(self):
        '''
        Loads camera preferences (matrix, distortion and projection matrix)
        from a file if it exists
        The filename is the camera MAC address
        :return:
        '''
        if os.path.isfile(self.macadress+'.npz'):
            file = np.load(self.macadress+'.npz')
            file.files
            self.camera_matrix = file['cam']
            self.distortion_coefficient = file['dist']
            self.projection_matrix = file['proj']
            print "Camera preference loaded"
            self.calibrated = True


    def saveCameraPreferences(self):
        '''
        Saves all cameras preferences (matrix, distortion and projection matrix)
        into a file
        The filename is the camera MAC address
        :return:
        '''
        if os.path.isfile(self.macadress+'.npz'):
            os.remove(self.macadress+'.npz')
        np.savez(self.macadress+'.npz', cam=self.camera_matrix, dist=self.distortion_coefficient, proj=self.projection_matrix)
        print "Camera preference saved"



    class New2DPointNotifier(Observable):
        '''
        Notify Observers (3D point) when a 2D point is created
        '''
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)

    class Point2DdeletedNotifier(Observable):
        '''
        Notify Observers (3D point) when a 2D point is deleted
        '''
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)


