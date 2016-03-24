#!/usr/bin/env python
import Point3D
from Tag import Tag

class User:
    """
    This class represents a User, with its position, tag
    """
    def __init__(self, server, client, mac):
        self.macadress = mac
        self.client = client
        self.server = server
        self.position = Point3D.Point3D(self)
        self.tag = None

    def sendPositionUpdate(self, position):
        """
        Send updated 3D position to the User over WebSocket
        :param position: Numpy Array containing X,Y,Z
        :return:
        """
        strPosition = str(position[0])+':'+str(position[1])+':'+str(position[2])
        self.server.send_message(self.client, strPosition)

    def setTag(self, tag):
        self.tag = tag
        self.tag.assign()

    def removeTag(self):
        if self.tag != None and isinstance(self.tag, Tag):
            print "Tag unassigned"
            self.tag.unAssign()
            self.tag = None

    def __del__(self):
        del self.position
        self.tag.unAssign()
