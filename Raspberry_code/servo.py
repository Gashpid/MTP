from adafruit_servokit import ServoKit
from sensors import ACCGYR,Encoder
import time,threading

class Motion():
    def __init__(self):
        self.config()
        self.initset()

    def config(self,*args):
        self.kit = ServoKit(channels=16, frequency = 60, reference_clock_speed=29000000)
        self.kit.servo[2].set_pulse_width_range(1000, 2000)
        self.PercentFineTuningFocus,self.PercentTuningFocus,self.focusStep = 0,0,0

    def ALT(self,angle):
        if(angle >= 0 and angle <= 135): self.kit.servo[1].angle = 10+(angle*105)/90
        
    def AZ(self,angle):
        self.kit.servo[3].angle = angle
        
    def FineTuningFocus(self,percent):
        self.kit.servo[2].angle = percent*180

    def initset(self,*args):
        self.kit.servo[0].angle = 70
        self.kit.servo[1].angle = 10
        f = open('assets/temp/db/TFDB.db','r')
        if(f.read() == 'True'):
            for i in range(4):
                self.kit.servo[0].angle = 90
                time.sleep(0.5)
                self.kit.servo[0].angle = 70
                time.sleep(0.05)
        f.close()
        
    def TuningFocus(self,percent):
        f = open('assets/temp/db/TFDB.db','w')
        if(percent == 0): f.write('False')
        else: f.write('True')
        f.close()
        enc,step,prestep,past,DirPilot = Encoder(),self.focusStep,0,0,0
        if(step < int((20*percent))+1 and self.focusStep < 21):
            self.kit.servo[0].angle = 0
            while True:
                prestep = enc.clockwise()
                
                if(prestep != None):
                    print(prestep)
                    step += prestep
                    if(step > int(20*percent) and step > past):
                        if(step > 20): self.focusStep = 21
                        else: self.focusStep = step
                        break
                else: self.kit.servo[0].angle = 70
                past = step
                time.sleep(0.01)
            self.kit.servo[0].angle = 70
            DirPilot = 1
            
        if(int(20*percent) < self.focusStep and DirPilot != 1):
            self.kit.servo[0].angle = 110
            while True:
                prestep = enc.clockwise()
                if(prestep != None):
                    step -= prestep
                    if(step < int(20*percent) and step < past):
                        if(step < 20): self.focusStep = step
                        else: self.focusStep = step
                        break
                past = step
                time.sleep(0.01)
            self.kit.servo[0].angle = 70
        #enc.close()
