import numpy as np
from parse import *
import compute

import Point2D
from utils.Observer import Observable


class Camera:

    camera_matrix = np.float64([[247.9139798, 0., 155.30251177], [0., 248.19822494, 100.74688813], [0.,  0., 1.]])
    distortion_coefficient = np.float64([-0.45977769,  0.29782977, -0.00162724,  0.00046035, -0.16351777])
    projection_matrix = np.array([], dtype=np.float32).reshape(0,3,4)
    pointsCalibration = np.array([], dtype=np.float32).reshape(0,2)

    MAX_DISTANCE_BETWEEN_POINTS = 10
    MAX_SIZE_DIFF_BETWEEN_POINTS = 5

    points2D = []

    def __init__(self, client):
        self.client = client
        self.new2DPointNotifier = Camera.New2DPointNotifier(self)
        self.point2DdeletedNotifier= Camera.Point2DdeletedNotifier(self)
        print
        #TODO try to load projection matrix

    def update(self, data):
        print data

    # Parse data from websocket to a dictionnay containing {'x': x, 'y': y, 'height': height, 'width': width};
    def parsePointMessage(self, data):
        extracted_data = parse("{id}x{x}y{y}h{h}w{w}a{a}", data)
        if len(extracted_data.named) == 6:
            return extracted_data.named
        else :
            return None

    def push(self, message):
        parsedPoint = self.parsePointMessage(message)
        if(parsedPoint != None):
            self.addPoint(parsedPoint['x'], parsedPoint['y'], parsedPoint['h'], parsedPoint['w'])

    # Track if the new point received correspond to a point already recorded (to follow the point)
    # Argument is the point data in an array outputed by "parse" function
    def addPoint(self, x, y, height, width):
        for point in self.points2D:
            if point.distance(x, y) < self.MAX_DISTANCE_BETWEEN_POINTS*self.MAX_DISTANCE_BETWEEN_POINTS and point.sizeDifference(height, width) < self.MAX_SIZE_DIFF_BETWEEN_POINTS*self.MAX_SIZE_DIFF_BETWEEN_POINTS :
                point.update(x, y, height, width)
                return
        # Point not found, add it to the list and notify creation :
        print("CAMERA : NEW 2D Point")
        newPoint = Point2D.Point2D(x, y, height, width)
        self.points2D.append(newPoint)
        self.new2DPointNotifier.notifyObservers()


    def enterCalibrationMode(self):
        projection_matrix = np.array([], dtype=np.float32).reshape(0,3,4)
        pointsCalibration = np.array([], dtype=np.float32).reshape(0,2)

    def exitCalibrationMode(self, world3DPoints):
        #TODO calculate matrix for each camera
        projection_matrix = compute.calculateProjectionMatrix(self, world3DPoints)

    def saveCalibrationPoint2D(self):
        self.pointsCalibration = np.append(self.pointsCalibration, self.points2D[-1], axis=0)
        print self.pointsCalibration



    class New2DPointNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)

    class Point2DdeletedNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)