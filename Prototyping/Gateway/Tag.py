class Tag:

    def __init__(self, server, client, mac):
        self.macadress = mac
        self.client = client
        self.server = server
        self.assigned = False
        self.setRGB(0,0,700)


    def isAssigned(self):
        return self.assigned

    def assign(self):
        self.assigned = True
        self.setIRonMax()
        self.setRGBoff()

    def unAssign(self):
        self.assigned = False
        self.setIRoff()
        self.setRGB(0,0,700)

    def setIRon(self):
        self.server.send_message(self.client, "on:0")

    def setIRonMax(self):
        self.server.send_message(self.client, "on:1")

    def setIRoff(self):
        self.server.send_message(self.client, "off")

    def pingIR(self):
        self.server.send_message(self.client, "offon")

    def setRGB(self, r, g, b):
        self.server.send_message(self.client, "rgb:" + str(r) + "-" + str(g) + "-" + str(b))

    def setRGBoff(self):
        self.server.send_message(self.client, "rgb:0-0-0")

    def debugUserTracked(self):
        self.setRGB(0,700,0)

    def debugUserLost(self):
        self.setRGB(700,0,0)

    def setCalibrationMode(self):
        self.setRGB(1023,500,0)

