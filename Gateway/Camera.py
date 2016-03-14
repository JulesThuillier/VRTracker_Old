import numpy as np
from parse import *
import compute
import os.path
from Point2D import Point2D
from utils.Observer import Observable


class Camera:

    MAX_DISTANCE_BETWEEN_POINTS = 10
    MAX_SIZE_DIFF_BETWEEN_POINTS = 10

    points2D = []

    def __init__(self, client, mac):
        self.client = client
        self.macadress = mac
        self.points2D = []
        self.new2DPointNotifier = Camera.New2DPointNotifier(self)
        self.point2DdeletedNotifier= Camera.Point2DdeletedNotifier(self)

        self.camera_matrix = np.float64([[247.9139798, 0., 155.30251177], [0., 248.19822494, 100.74688813], [0.,  0., 1.]])
        self.distortion_coefficient = np.float64([-0.45977769,  0.29782977, -0.00162724,  0.00046035, -0.16351777])
        self.projection_matrix = np.array([], dtype=np.float32).reshape(0,3,4)
        self.pointsCalibration = np.array([], dtype=np.float32).reshape(0,2)

        self.loadCameraPreferences()



    # Parse data from websocket to a dictionnay containing {'x': x, 'y': y, 'height': height, 'width': width};
    def parsePointMessage(self, data):
        extracted_data = parse("{id}x{x}y{y}h{h}w{w}a{a}", data)
        if len(extracted_data.named) == 6:
            return extracted_data.named
        else :
            return None

    def push(self, message):
        print "\nPushed from : "
        print self.client['address']
        parsedPoint = self.parsePointMessage(message)
        if(parsedPoint != None):
            self.addPoint(parsedPoint['x'], parsedPoint['y'], parsedPoint['h'], parsedPoint['w'])

    # Track if the new point received correspond to a point already recorded (to follow the point)
    # Argument is the point data in an array outputed by "parse" function
    def addPoint(self, x, y, height, width):
        updated = False
        for point in self.points2D:
            if point.distance(x, y) < self.MAX_DISTANCE_BETWEEN_POINTS*self.MAX_DISTANCE_BETWEEN_POINTS and point.sizeDifference(height, width) < self.MAX_SIZE_DIFF_BETWEEN_POINTS*self.MAX_SIZE_DIFF_BETWEEN_POINTS :
                point.update(x, y, height, width)
                updated = True
            else:
                point.count()
                # Remove lost points
                if point.isLost():
                    print '------------ Lost --------------'
                    self.points2D.remove(point)
        # Point not found, add it to the list and notify creation :
        if updated==False:
            print("CAMERA : NEW 2D Point  - " + str(x) + " - " + str(y))
            print self.points2D
            newPoint = Point2D(x, y, height, width, self)
            self.points2D.append(newPoint)
            self.new2DPointNotifier.notifyObservers()


    def enterCalibrationMode(self):
        projection_matrix = np.array([], dtype=np.float32).reshape(0,3,4)
        pointsCalibration = np.array([], dtype=np.float32).reshape(0,2)

    def exitCalibrationMode(self, world3DPoints):
        print self.client['id']
        print self.pointsCalibration
        print world3DPoints
        self.projection_matrix = compute.calculateProjectionMatrix(self, world3DPoints)
        self.saveCameraPreferences()

    def saveCalibrationPoint2D(self):
        xy = [self.points2D[-1].buffer[-1]['x'], self.points2D[-1].buffer[-1]['y']]
        self.pointsCalibration = np.append(self.pointsCalibration, [xy], axis=0)

    def loadCameraPreferences(self):
        if os.path.isfile(self.macadress+'.npz'):
            file = np.load(self.macadress+'.npz')
            file.files
            self.camera_matrix = file['cam']
            self.distortion_coefficient = file['dist']
            self.projection_matrix = file['proj']
            print "Camera preference loaded"


    def saveCameraPreferences(self):
        if os.path.isfile(self.macadress+'.npz'):
            os.remove(self.macadress+'.npz')
        np.savez(self.macadress+'.npz', cam=self.camera_matrix, dist=self.distortion_coefficient, proj=self.projection_matrix)
        print "Camera preference saved"



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