import serial,smbus,sys
from time import sleep
from RPi import GPIO

class GPS():
    def __init__(self):
        self.serialPort = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)

    def parseGPS(self,string):
        date = string[9][:2]+'/'+string[9][2:4]+'/20'+string[9][4:6]
        lat = str(int(string[3][:2]))+'°'+string[3][2:4]+'\u0027'+str(float('0'+string[3][4:])*60)[:2]+'"'+string[4]
        lon = str(int(string[5][:3]))+'°'+string[5][3:5]+'\u0027'+str(float('0'+string[5][5:])*60)[:2]+'"'+string[6]
        return [lat,lon,date]
        #print("Lat: %s -- Lon: %s -- Date: %s" % (lat,lon,date))

    def run(self,*args):
        GPSData = []
        while True:
            try:
                string = self.serialPort.readline(); string = str(string)[2:len(string)-1]; string = string.split(',')
                if(string[0] == '$GPRMC' and string[2] == 'A'): GPSData = self.parseGPS(string); return GPSData; break
            except KeyboardInterrupt: sys.exit(0)

class ACCGYR():
    def __init__(self):
        self.registers()
        self.bus = smbus.SMBus(1)
        self.Device_Address = 0x68 # MPU6050 device address
        self.MPU_Init()
        
    def registers(self,*args):
        #some MPU6050 Registers and their Address
        self.PWR_MGMT_1   = 0x6B
        self.SMPLRT_DIV   = 0x19
        self.CONFIG       = 0x1A
        self.GYRO_CONFIG  = 0x1B
        self.INT_ENABLE   = 0x38
        self.ACCEL_XOUT_H = 0x3B
        self.ACCEL_YOUT_H = 0x3D
        self.ACCEL_ZOUT_H = 0x3F
        self.GYRO_XOUT_H  = 0x43
        self.GYRO_YOUT_H  = 0x45
        self.GYRO_ZOUT_H  = 0x47

    def MPU_Init(self,*args):
            #write to sample rate register
            self.bus.write_byte_data(self.Device_Address, self.SMPLRT_DIV, 7)
            #Write to power management register
            self.bus.write_byte_data(self.Device_Address, self.PWR_MGMT_1, 1)
            #Write to Configuration register
            self.bus.write_byte_data(self.Device_Address, self.CONFIG, 0)
            #Write to Gyro configuration register
            self.bus.write_byte_data(self.Device_Address, self.GYRO_CONFIG, 24)
            #Write to interrupt enable register
            self.bus.write_byte_data(self.Device_Address, self.INT_ENABLE, 1)

    def read_raw_data(self,addr):
            #Accelero and Gyro value are 16-bit
            high = self.bus.read_byte_data(self.Device_Address, addr)
            low = self.bus.read_byte_data(self.Device_Address, addr+1)
            #concatenate higher and lower value
            value = ((high << 8) | low)
            #to get signed value from mpu6050
            if(value > 32768): value = value - 65536
            return value
    
    def run(self,*args):
        #Read Accelerometer raw value
        acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
        acc_y = self.read_raw_data(self.ACCEL_YOUT_H)
        acc_z = self.read_raw_data(self.ACCEL_ZOUT_H)
        
        #Read Gyroscope raw value
        gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
        gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
        gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)
        
        #Full scale range +/- 250 degree/C as per sensitivity scale factor
        Ax = acc_x/16384.0
        Ay = acc_y/16384.0
        Az = acc_z/16384.0
        Gx = gyro_x/131.0
        Gy = gyro_y/131.0
        Gz = gyro_z/131.0

        return [Ax,Ay,Az,Gx,Gy,Gz]
        #print ("Gx=%.2f" %Gx, u'\u00b0'+ "/s", "\tGy=%.2f" %Gy, u'\u00b0'+ "/s", "\tGz=%.2f" %Gz, u'\u00b0'+ "/s", "\tAx=%.2f g" %Ax, "\tAy=%.2f g" %Ay, "\tAz=%.2f g" %Az) 	


class Encoder():
    def __init__(self):
        self.config()

    def config(self,*args):
        self.step = 1; GPIO.setmode(GPIO.BCM) 
        GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.counter,self.clkLastState,self.dtLastState = 0,GPIO.input(17),GPIO.input(18)

    def clockwise(self,*args):
            self.clkState,self.dtState = GPIO.input(17),GPIO.input(18)
            if(self.clkState == 0 and self.dtState == 1): self.counter = self.counter + self.step; return self.counter
            else: return None

    def counterclockwise(self,*args):
            self.clkState,self.dtState = GPIO.input(17),GPIO.input(18)
            if(self.clkState == 1 and self.dtState == 0): self.counter = self.counter - self.step; return self.counter
            else: return None

    def close(self,*args): GPIO.cleanup()
