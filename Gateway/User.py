import Point3D


class User:
    """
    This class represents a User, with its position, tag
    """
    def __init__(self, client, server):
        self.client = client
        self.server = server
        self.position = Point3D.Point3D(self)

    def sendPositionUpdate(self, position):
        """
        Send updated 3D position to the User over WebSocket
        :param position:
        :return:
        """
        self.server.send_message(self.client, position)