from websocket_server import WebsocketServer
from camera import Camera
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

            elif message == "tag":
                del self.unknown[str(client['address'])]
                # TODO

            elif message == "user":
                del self.unknown[str(client['address'])]
                self.users[str(client['address'])] = User.User(str(client['address']))
