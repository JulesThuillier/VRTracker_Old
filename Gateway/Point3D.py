from Camera import Camera
from utils.Observer import Observer


# Represent a 3D Position with observers on 2D point updates
class Point3D():

    points2D = []

    def __init__(self):
        print "Init Point 3D"

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
        lastxy = buffer[-1]
        distx = abs(lastxy[0] - x)
        disty = abs(lastxy[1] - y)
        distz = abs(lastxy[2] - z)
        return distx*distx + disty*disty + distz*distz


    class point2DUpdateObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("Position update Observer in Point 3D")
            #TODO Calculate 3D position


    class newPoint2DObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("New 2D Point Observer in Point 3D")
            if isinstance(arg, Camera):

                #TODO check if this point could be owned by this user, if yes add it to the list
                print ("points2D length : " + str(len(self.outer.points2D)))
                self.outer.add(arg)
                print ("points2D length after add : " + str(len(self.outer.points2D)))

                # Add Observer for position update on 2D Point from Camera
                arg.positionUpdateNotifier.addObserver(self.outer.point2DUpdateObserver)

    class point2DDeletedObserver(Observer):
        def __init__(self, outer):
            self.outer = outer
        def update(self, observable, arg):
            print("2D Point deleted Observer in Point 3D")
            if isinstance(arg, Camera):
                print ("points2D length : " + str(len(self.outer.points2D)))
                self.outer.delete(arg)
                print ("points2D length after remove : " + str(len(self.outer.points2D)))
                # Remove Observer for position update on 2D Point from Camera
                arg.positionUpdateNotifier.deleteObserver(self.outer.point2DUpdateObserver)