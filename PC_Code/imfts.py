from PIL import Image, ImageChops
import cv2, os, shutil
import numpy as np
import threading

class Laplacian():
    def __init__(self):
        f = open('assets/config/config.txt', 'r'); self.config = f.read(); f.close()
        self.config = self.config.split(','); self.config[3] = float(self.config[3])

    def getLP(self, image):
        dst = cv2.filter2D(image,-1,np.array([[0,0,0],[0,1/(9*self.config[3]),0],[0,0,0]]))
        conv = cv2.Laplacian(dst, cv2.CV_64F)
        return [conv,conv.var()*9*self.config[3]]

class LongExposure():
    def __init__(self):
        self.pathin,self.pathout = os.getcwd()+'/assets/temp/imTP',os.getcwd()+'/assets/temp/imsum.png'
        f = open('assets/config/config.txt', 'r'); self.config = f.read(); f.close()
        self.config = self.config.split(','); self.config[0] = int(self.config[0])
        self.folder = os.getcwd()+'/assets/temp/imTP'
        self.erasepath(); self.imcount = 0

    def erasepath(self):
        for the_file in os.listdir(self.folder):
               file_path = os.path.join(self.folder, the_file)
               try:
                   if os.path.isfile(file_path): os.unlink(file_path)
               except: pass

    def imsum(self):
        images = [os.path.join(self.pathin, x) for x in os.listdir(self.pathin)]
        result = Image.open(images[0])
        for i in range(1, len(images) - 1):
            image = Image.open(images[i])
            result = ImageChops.lighter(result, image)
        result.save(self.pathout)

    def getLE(self, image):
        cv2.imwrite(self.folder+'/temp'+str(self.imcount)+'.png',image); self.imcount += 1
        if(self.imcount > self.config[0]): self.imcount = 0; self.erasepath()
        elif(self.imcount == self.config[0]): thread = threading.Thread(target = self.imsum()); thread.start()

class SkyMap():
    def __init__(self):
        self.pathin,self.pathout = os.getcwd()+'/assets/temp/SkyMapImages/BeforeLP',os.getcwd()+'/assets/temp/SkyMapImages/AfterLP'
        f = open('assets/config/config.txt', 'r'); self.config = f.read(); f.close(); self.config = self.config.split(',')
        self.config[0],self.config[1],self.config[2] = int(self.config[0]),int(self.config[1]),int(self.config[2])
        self.erasepath(self.pathin); self.erasepath(self.pathout); self.imcount,self.imout = 0,0
        
    def erasepath(self, path):
        for the_file in os.listdir(path):
               file_path = os.path.join(path, the_file)
               try:
                   if os.path.isfile(file_path): os.unlink(file_path)
               except: pass

    def imsumLE(self):
        images = [os.path.join(self.pathin, x) for x in os.listdir(self.pathin)]
        result = Image.open(images[0])
        for i in range(1, len(images) - 1):
            image = Image.open(images[i])
            result = ImageChops.lighter(result, image)
        result.save(self.pathout+'/'+str(self.imout)+'.png')

    def skymapbuild(self):
        images = os.listdir(self.pathout)

    def build(self, image):
        cv2.imwrite(self.pathin+'/'+str(self.imcount)+'.png',image); self.imcount += 1
        if(self.imcount > self.config[0]): self.imcount = 0; self.erasepath(self.pathin)
        elif(self.imcount == self.config[0]): thread = threading.Thread(target = self.imsumLE()); thread.start(); self.imout += 1
        
sm = SkyMap()

for i in range(100):
    im = cv2.imread('C:/Users/gizqu/OneDrive/Escritorio/imTP2/'+str(i)+'.png',0)
    sm.build(im)
