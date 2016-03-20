#!/usr/bin/env python
from Camera import Camera
from utils.Observer import Observer
from Point2D import Point2D
import compute


# Represent a 3D Position with observers on 2D point updates
class Point3D:

    MAX_DISTANCE_ERROR = 30

    def __init__(self, user):
        print "Init Point 3D"
        self.lastXYZ = []
        self.points2D = []
        self.user = user
        self.newPoint2DObserver = Point3D.NewPoint2DObserver(self)
        self.point2DDeletedObserver = Point3D.Point2DDeletedObserver(self)
        self.point2DUpdateObserver = Point3D.Point2DUpdateObserver(self)

    def update(self):
        print ("TODO")

    def add(self,point2D):
        self.points2D.append(point2D)

    def delete(self,point2D):
        self.points2D.remove(point2D)

    # Warning : does not pop
    def get(self):
        return buffer[-1]

    def getAll(self):
        return list(buffer)


    # Check distance between last 3D point in buffer and the point in parameter (not squared)
    def distance(self, x, y, z):
        distx = abs(self.lastXYZ[0,0] - x)
        disty = abs(self.lastXYZ[1,0] - y)
        distz = abs(self.lastXYZ[2,0] - z)
        return distx*distx + disty*disty + distz*distz


    class Point2DUpdateObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
#            print("Position update Observer in Point 3D")
            #TODO Calculate 3D position
            if len(self.outer.points2D) > 1:
                new3Dposition = compute.calculate3DPosition(self.outer.points2D[len(self.outer.points2D)-1], self.outer.points2D[len(self.outer.points2D)-2])
                self.outer.user.sendPositionUpdate(new3Dposition)
                self.lastXYZ = new3Dposition


    class NewPoint2DObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
#            print("New 2D Point Observer in Point 3D")
            if isinstance(observable.outer, Camera):
                #TODO check if this point could be owned by this user, if yes add it to the list
                temp2D = observable.outer.points2D[-1]

                # 1: Check if new 2D Point comes from same camera as another 2D Point used here (if yes, discard)
                for point in self.outer.points2D:
                    if point.camera == temp2D.camera:
                        print "2D Point discard : same camera"
                        return

                # 2: Calculate 3D Point position with new 2D point and check position difference (yes difference too high, discard)
                for point in self.outer.points2D:
                    temp3D = compute.calculate3DPosition(point, temp2D)
                    if(self.outer.distance(temp3D[0,0], temp3D[1,0], temp3D[2,0]) > self.outer.MAX_DISTANCE_ERROR*self.outer.MAX_DISTANCE_ERROR):
                        print "2D Point discard : too far"
                        return

                # Add the New 2D Point to this 3D Point
                self.outer.add(temp2D)
                # Add Observer for position update on last 2D Point added from Camera
                observable.outer.points2D[-1].positionUpdateNotifier.addObserver(self.outer.point2DUpdateObserver)

    class Point2DDeletedObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("2D Point deleted Observer in Point 3D")
            if isinstance(arg, Camera):
 #               print ("points2D length : " + str(len(self.outer.points2D)))
                self.outer.delete(arg)
  #              print ("points2D length after remove : " + str(len(self.outer.points2D)))
                # Remove Observer for position update on 2D Point from Camera
                observable.outer.points2D[-1].positionUpdateNotifier.deleteObserver(self.outer.point2DUpdateObserver)
