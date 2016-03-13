from websocket_server import WebsocketServer

import Camera
from tracking import User


class websocketserver():

    cameras = {}
    tags = {}
    users = {}

    port=8001

    # Called for every client connecting (after handshake)
    def new_client_connection(self, client, server):
        print("New client connected and was given id %d" %  client['id'] +" and  address " + str(client['address']))
        server.send_message_to_all("Hey all, a new client has joined us")


    # Called for every client disconnecting
    def client_left(self, client, server):
        print("Hello left")
        #print("Client(%d) disconnected" % client['id'])

    # Called when a client sends a message
    def message_received(self, client, server, message):
        print("Client(%d) said: %s" % (client['id'], message))
        self.parseMessage(client, message)

    def __init__(self, host='127.0.0.1'):
        server = WebsocketServer(self.port, host)
        server.set_fn_new_client(self.new_client_connection)
        server.set_fn_client_left(self.client_left)
        server.set_fn_message_received(self.message_received)
        server.run_forever()


    def parseMessage(self, client, message):
        if self.cameras.has_key(str(client['address'])):
            print "Message from Camera"
            self.cameras[str(client['address'])].parse(message)

        elif self.users.has_key(str(client['address'])):
            print "Message from User"

        elif self.tags.has_key(str(client['address'])):
            print "Message from Tag"

        else:
            if message == "camera":
                self.cameras[str(client['address'])] = Camera.Camera(str(client['address']))
                # Add Observers linking every user to every camera's update
                for user in self.users:
                    self.cameras[str(client['address'])].new2DPointNotifier.addObserver(user.position.newPoint2DObserver)
                    self.cameras[str(client['address'])].point2DdeletedNotifier.addObserver(user.position.point2DDeletedObserver)

            elif message == "tag":
                del self.unknown[str(client['address'])]
                # TODO

            elif message == "user":
                del self.unknown[str(client['address'])]
                self.users[str(client['address'])] = User.User(str(client['address']))
                # Add Observers linking every user to every camera's update
                for camera in self.cameras:
                    camera.new2DPointNotifier.addObserver(self.users[str(client['address'])].position.newPoint2DObserver)
                    camera.point2DdeletedNotifier.addObserver(self.users[str(client['address'])].position.point2DDeletedObserver)
