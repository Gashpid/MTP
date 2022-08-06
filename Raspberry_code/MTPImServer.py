import zmq, cv2, base64, socket
import numpy as np
import threading
from imdef import getFrame
from sensors import GPS
from servo import Motion

class Transeiver():
    def __init__(self):
        self.context = zmq.Context()
        self.socketZMQ = self.context.socket(zmq.REP)
        self.socketZMQ.bind('tcp://'+self.getHost()+':6000')

        self.message = b''
        self.run()

    def getHost(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        hostname = s.getsockname()[0]
        s.close()
        return hostname

    def run(self):
        print('Running...')
        move = Motion()
        while True:
            self.message = self.socketZMQ.recv()
            self.message = self.message.decode()
            if(self.message == 'init'):
                gps = GPS(); gpsdata = None
                while gpsdata == None: gpsdata = gps.run()
                self.socketZMQ.send_string('LL,'+gpsdata[0]+','+gpsdata[1]); init = 1
            elif(self.message[:3] == 'ALT'): self.socketZMQ.send_string('DR'); threading.Thread(target = move.ALT, args = (float(self.message[3:]),)).start()
            #elif(self.message[:2] == 'TF'): self.socketZMQ.send_string('DR'); threading.Thread(target = move.TuningFocus, args = (float(self.message[2:]),)).start()
            elif(self.message[:3] == 'FTF'): self.socketZMQ.send_string('DR'); threading.Thread(target = move.FineTuningFocus, args = (float(self.message[3:]),)).start()
            #else: self.socketZMQ.send_string('DR')

class imageSend():
    def __init__(self):
        self.context = zmq.Context()
        self.socketZMQ = self.context.socket(zmq.REP)
        self.socketZMQ.bind('tcp://'+self.getHost()+':5555')

        self.message = b''
        self.run()

    def getHost(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        hostname = s.getsockname()[0]
        s.close()
        return hostname
        
    def imEncode(self):
        
        image = open('assets/temp/image/imtemp.png','rb')
        image_read = image.read()
        image_64_encode = base64.encodebytes(image_read)
        image_64_encode = image_64_encode.decode()
        return image_64_encode

    def imSend(self):
        ret = getFrame()
        if(ret == False):
            self.socketZMQ.send_string('01E')
            print('Image stopped...')
        else:
            frame2send = self.imEncode()
            self.socketZMQ.send_string(frame2send)


    def run(self):
        print('Running...')
        while True:
            self.message = self.socketZMQ.recv()
            if self.message == b'1': self.imSend()


Threads = [threading.Thread(target = imageSend),threading.Thread(target = Transeiver)]
Threads[0].start(); Threads[1].start()
