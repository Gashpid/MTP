import cv2

cam = cv2.VideoCapture(0)


def getFrame(*args):
    ret,frame = cam.read()
    if(ret == True): cv2.imwrite('assets/temp/image/imtemp.png', frame)
    return ret
