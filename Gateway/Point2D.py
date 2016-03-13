from collections import deque
from utils.Observer import Observer, Observable
from math import sqrt

# Buffer of a 2D point
class Point2D():

    origin = "" # IP of the camera that recorded this point

    bufferSize = 50
    buffer = deque(maxlen=bufferSize)

    def __init__(self, x, y, height, width):
        point = {'x': x, 'y': y, 'height': height, 'width': width};
        buffer.append(point)
        #TODO Notify point created ==> To associate it to 3D point

    def update(self, x, y, height, width):
        point = {'x': x, 'y': y, 'height': height, 'width': width};
        buffer.append(point)
        #TODO Notify 2D Point updated ==> Update 3D position
        self.positionUpdateNotifier.notifyObservers()

    # Warning : does not pop
    def get(self):
        return buffer[-1]

    def getAll(self):
        return list(buffer)


    # Check distance between last 2D point in buffer and the point in parameter (not squared)
    def distance(self, x, y):
        lastxy = buffer[-1]
        distx = abs(lastxy[0] - x)
        disty = abs(lastxy[1] - y)
        return distx*distx + disty*disty

    # Check distance between last 2D point in buffer and the point in parameter (not squared)
    def sizeDifference(self, height, width):
        lastxy = buffer[-1]
        h = abs(lastxy[2] - height)
        w = abs(lastxy[3] - width)
        return h*h + w*w


    class positionUpdateNotifier(Observable):
        def __init__(self, outer):
            Observable.__init__(self)
            self.outer = outer
        def notifyObservers(self):
                self.setChanged()
                Observable.notifyObservers(self)
