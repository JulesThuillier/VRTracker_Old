#!/usr/bin/env python
from websocket_server import WebsocketServer
from Camera import Camera
from User import User
from Calibration import Calibration
from Tag import Tag


class websocketserver:

    cameras = {}
    tags = {}
    users = {}
    calibration = {}

    port=8001

    # Called for every client connecting (after handshake)
    def new_client_connection(self, client, server):
        print("New client connected and was given id %d" %  client['id'] +" and  address " + str(client['address']))
        server.send_message(client, "Client connected succesfully")


    # Called for every client disconnecting
    def client_left(self, client, server):
        print("Client(%d) disconnected" % client['id'])
        # Remove client from its list
        # TODO better delete (remove points etc...)

        if(str(client['address']) in self.cameras):
            del self.cameras[str(client['address'])]

        elif(str(client['address']) in self.users):
            # Remove Tag assignement because User left
            self.users[str(client['address'])].removeTag()
            del self.users[str(client['address'])]

        elif(str(client['address']) in self.calibration):
            del self.calibration[str(client['address'])]

        elif(str(client['address']) in self.tags):
            # Remove Tag assignement to User because Tag left
            for key in self.users:
                if self.users[key].tag == self.tags[str(client['address'])]:
                    self.users[key].removeTag()
            del self.tags[str(client['address'])]


    # Called when a client sends a message
    def message_received(self, client, server, message):
        self.parseMessage(client, message)

    def __init__(self, host='127.0.0.1'):
        self.server = WebsocketServer(self.port, host)
        self.server.set_fn_new_client(self.new_client_connection)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)
        self.server.run_forever()


    def parseMessage(self, client, message):
        """
        Check who is the message from to redirect it to User / Tag / Camera / Calibration
        or create a new instance of User / Tag / Camera / Calibration
        :param client:
        :param message:
        :return:
        """
        if self.cameras.has_key(str(client['address'])):
            #print "Message from Camera"
            self.cameras[str(client['address'])].push(message)

        elif self.users.has_key(str(client['address'])):
            print "Message from User"

        elif self.tags.has_key(str(client['address'])):
            print "Message from Tag"

        elif self.calibration.has_key(str(client['address'])):
            self.calibration[str(client['address'])].push(message)
            print "Message from Calibration"

        # This message is coming from an unknown client
        else:
            if message.split("-")[0] == "camera":
                self.cameras[str(client['address'])] = Camera(client, message.split("-")[1])
                # Add Observers linking every user to every camera's update
                for key in self.users:
                    if isinstance(self.users[key], User):
                        self.cameras[str(client['address'])].new2DPointNotifier.addObserver(self.users[key].position.newPoint2DObserver)
                        self.cameras[str(client['address'])].point2DdeletedNotifier.addObserver(self.users[key].position.point2DDeletedObserver)

            elif message.split("-")[0] == "tag":
                self.tags[str(client['address'])] = Tag(self.server, client, message.split("-")[1])
                for key in self.users:
                    if isinstance(self.users[key], User):
                        # Assign a Tag to User with no Tag
                        if self.users[key].tag == None:
                            self.users[key].setTag(self.tags[str(client['address'])])

            elif message.split("-")[0] == "user":
                user = User(self.server, client, message.split("-")[1])
                self.users[str(client['address'])] = user
                # Add Observers linking every user to every camera's update
                for key in self.cameras:
                    if isinstance(self.cameras[key], Camera):
                        self.cameras[key].new2DPointNotifier.addObserver(user.position.newPoint2DObserver)
                        self.cameras[key].point2DdeletedNotifier.addObserver(user.position.point2DDeletedObserver)

                for key in self.tags:
                    if isinstance(self.tags[key], Tag):
                        # Assign a Tag to new User
                        if self.tags[key].isAssigned() == False:
                            user.setTag(self.tags[key])

            elif message == "calibration":
                if(len(self.tags)>0):
                    self.calibration[str(client['address'])] = Calibration(self.server, client, self.cameras, self.tags.values()[0])
                else:
                    self.server.send_message(client, "Please connect a Tag first, and start Calibration again.")

