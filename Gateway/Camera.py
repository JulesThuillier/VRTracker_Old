import numpy as np
from parse import *
from tracking import Point2D
from utils.Observer import Observer, Observable

class Camera():

    ip = ""
    camera_matrix = np.float64([[247.9139798, 0., 155.30251177], [0., 248.19822494, 100.74688813], [0.,  0., 1.]])
    distortion_coefficient = np.float64([-0.45977769,  0.29782977, -0.00162724,  0.00046035, -0.16351777])

    MAX_DISTANCE_BETWEEN_POINTS = 10
    MAX_SIZE_DIFF_BETWEEN_POINTS = 5

    points2D = []

    def __init__(self, ipCam):
        self.ip = ipCam

    def update(self, data):
        print data

    # Parse data from websocket to a dictionnay containing {'x': x, 'y': y, 'height': height, 'width': width};
    def parse(self, data):
        extracted_data = parse("{}x{}y{}h{}w{}a{}", data)
        if len(extracted_data) == 6:
            new_point = {'x': extracted_data[1], 'y': extracted_data[2], 'height': extracted_data[3], 'width': extracted_data[4]};
            return new_point
        else :
            return None


    # Track if the new point received correspond to a point already recorded (to follow the point)
    # Argument is the point data in an array outputed by "parse" function
    def addPoint(self, x, y, height, width):
        for point in self.points2D:
            if point.distance(x, y) < self.MAX_DISTANCE_BETWEEN_POINTS*self.MAX_DISTANCE_BETWEEN_POINTS and point.sizeDifference(height, width) < self.MAX_SIZE_DIFF_BETWEEN_POINTS*self.MAX_SIZE_DIFF_BETWEEN_POINTS :
                point.update(x, y, height, width)
                return
        # Point not found, add it to the list and notify creation :
        print("CAMERA " + self.ip + " : NEW 2D Point")
        self.points2D.append(Point2D(x, y, height, width))
        self.new2DPointNotifier.notifyObservers()


    class new2DPointNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)

    class point2DdeletedNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)