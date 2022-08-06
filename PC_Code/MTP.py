from PIL import ImageTk, Image
import tkinter as tk
import os, cv2, zmq
import numpy as np
import base64
import socket
import tkinter.font as tkFont


class MTPrx():
    def startSocket(self):
        HOST = '192.168.137.207'
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect('tcp://'+HOST+':5555')

        self.contextZMQCLI = zmq.Context()
        self.sockZMQCLI = self.contextZMQCLI.socket(zmq.REQ)
        self.sockZMQCLI.connect('tcp://'+HOST+':6000')

        self.getTelemetry()
        self.root.bind("<KP_5>", self.ALTInc)

    def getTelemetry(self):
        self.sockZMQCLI.send_string('init')
        data = self.sockZMQCLI.recv()
        data = data.decode()
        data = data.split(',')
        if(data[0] == 'LL'): self.GPS_var.set(data[1]+' , '+data[2])
        
    def __init__(self):
        self.Bx,self.By = 0,0
        self.AR,self.AZ = 0,0
        self.TF,self.FTF = '',''
        self.DEC,self.ALT = 0,0
        
        self.root = tk.Tk()
        self.root.minsize(1280,720)
        self.root.config(bg = '#000000')
        

        menu = tk.Menu(self.root)
        self.root.config(menu = menu)
        Ops = tk.Menu(menu, tearoff=0)
        Ops.config(bg='GREEN')
        Ops.add_command(label='Connect', command = self.startSocket)
        Ops.add_command(label='Start', command = self.ImageRx)
        menu.add_cascade(label='Conection', menu=Ops)
        config = tk.Menu(menu, tearoff=0)
        config.add_command(label = 'Set configuration', command = self.setconfigww)
        menu.add_cascade(label='Configure', menu = config)

        imSeptentrion = ImageTk.PhotoImage(Image.open('assets/images/septentrion.png').resize((60, 60)))
        SeptentrionimL = tk.Label(self.root, image = imSeptentrion, bg = '#000000')
        SeptentrionimL.place(relx = 0.02, rely = 0.02, width = 60, height = 60)

        self.Cardinal_var = tk.StringVar()
        CardinalOrientation = tk.Entry(self.root, textvariable = self.Cardinal_var, bd = 0, bg = '#000000', fg = '#0000FF')
        CardinalOrientation.place(relx = 0.068, rely = 0.045, relwidth = 0.15, height = 22)

        imGeographicalPosition = ImageTk.PhotoImage(Image.open('assets/images/GP.png').resize((40, 50)))
        GeographicalPositionimL = tk.Label(self.root, image = imGeographicalPosition, bg = '#000000')
        GeographicalPositionimL.place(relx = 0.02, rely = 0.14, width = 60, height = 60)

        self.GPS_var = tk.StringVar()
        GPS = tk.Entry(self.root, textvariable = self.GPS_var, bd = 0, bg = '#000000', fg = '#0000FF')
        GPS.place(relx = 0.068, rely = 0.17, relwidth = 0.15, height = 22)

        imStarCoor = ImageTk.PhotoImage(Image.open('assets/images/starcoor.jpg').resize((40, 50)))
        StarCoorimL = tk.Label(self.root, image = imStarCoor, bg = '#000000')
        StarCoorimL.place(relx = 0.02, rely = 0.26, width = 60, height = 70)

        self.StarCoor = tk.Text(self.root, bd = 0, bg = '#000000', fg = '#0000FF')
        self.StarCoor.config(font=("Consolas",11), padx = 5, pady = 5)
        self.StarCoor.place(relx = 0.068, rely = 0.26, relwidth = 0.13, height = 85)
        self.writeStarCoor()

        self.Mode_var = tk.StringVar(); self.Mode_var.set('Auto')
        self.Mode = tk.Label(self.root, textvariable = self.Mode_var, bg = '#2A900A', fg = '#000000')
        self.Mode.place(relx = 0.199, rely = 0.26, relwidth = 0.05, height = 85)
        self.Mode.bind('<Button-1>', self.ModeE)
        self.ModeTogle = 0

        self.TFC=tk.Canvas(self.root, width=140, height=36, background='#272727')
        self.TFC.place(relx = 0.02, rely = 0.4)
        self.TFC.bind("<ButtonPress-1>",self.bPTF)
        self.TFC.bind("<Motion>", self.mmTF)
        self.TFC.bind("<ButtonRelease-1>",self.bLeaveF)
        self.TFC.create_rectangle(0,0,5,40, width = 5,fill='#000445')
        self.TFC.create_text(70,18,fill='#C70039',font="Times 10 italic bold",text="Tuning focus 0")

        self.FTFC=tk.Canvas(self.root, width=144, height=36, background='#272727')
        self.FTFC.place(relx = 0.134, rely = 0.4)
        self.FTFC.bind("<ButtonPress-1>",self.bPTF)
        self.FTFC.bind("<Motion>", self.mmFTF)
        self.FTFC.bind("<ButtonRelease-1>",self.bLeaveF)
        self.FTFC.create_rectangle(0,0,5,40, width = 5,fill='#000445')
        self.FTFC.create_text(72,18,fill='#C70039',font="Times 10 italic bold",text="Fine tuning focus 0")
        self.pressed=False

        self.background_image = ImageTk.PhotoImage(Image.open('assets\images\starcoor.jpg'))
        self.canvas=tk.Canvas(self.root,  width=292, height=200, bd = 0, highlightthickness=0, relief='ridge', background="black")
        self.canvas.create_image(146, 100, image=self.background_image)
        self.canvas.place(relx = 0.02, rely = 0.47)
        self.canvas.bind("<ButtonPress-1>",self.B1_Pressed)
        self.canvas.bind("<ButtonPress-3>",self.B3_Pressed)
        self.canvas.bind("<Motion>", self.move_mouse)
        self.canvas.bind("<ButtonRelease-1>",self.botton_leave)
        self.canvas.bind("<ButtonRelease-3>",self.botton_leave)
        self.B1pressed=False
        self.B2pressed=False

        imUp = ImageTk.PhotoImage(Image.open('assets/images/up_arrow.png').resize((40,40)))
        imDwn = ImageTk.PhotoImage(Image.open('assets/images/down_arrow.png').resize((40,40)))
        imLeft = ImageTk.PhotoImage(Image.open('assets/images/left_arrow.png').resize((40,40)))
        imRight = ImageTk.PhotoImage(Image.open('assets/images/right_arrow.png').resize((40,40)))
        
        self.BUp = tk.Label(self.root, image = imUp, bg = '#000000', bd = 0, text='up')
        self.BLT = tk.Label(self.root, image = imLeft, bg = '#000000', bd = 0, text='left')
        self.BRT = tk.Label(self.root, image = imRight, bg = '#000000', bd = 0, text='right')
        self.BDn = tk.Label(self.root, image = imDwn, bg = '#000000', bd = 0, text='down')

        self.BUp.place(relx = 0.06+0.055, rely = 0.77, width = 50, height = 45)
        self.BLT.place(relx = 0.02+0.055, rely = 0.83, width = 50, height = 45)
        self.BRT.place(relx = 0.1+0.055, rely = 0.83, width = 50, height = 45)
        self.BDn.place(relx = 0.06+0.055, rely = 0.89, width = 50, height = 45)

        self.BUp.bind('<Button-1>', self.ALTInc)
        self.BLT.bind('<Button-1>', self.AZInc)
        self.BRT.bind('<Button-1>', self.AZDec)
        self.BDn.bind('<Button-1>', self.ALTDec)

        StartFrame = ImageTk.PhotoImage(Image.open('assets/images/MTP-Model.png').resize((394,640)))
        self.imL = tk.Label(self.root, image = StartFrame, bg = '#000000')
        self.imL.place(relx = 0.25, rely = 0.02, relwidth = 0.5, relheight = 0.95)

        StartLS = ImageTk.PhotoImage(Image.open('assets/images/MTP-Model.png').resize((194,240)))
        self.imLS = tk.Label(self.root, image = StartLS, bg = '#000000')
        self.imLS.place(relx = 0.75, rely = 0.02+0.16, relwidth = 0.24, relheight = 0.25)

        StartStarMap = ImageTk.PhotoImage(Image.open('assets/images/MTP-Model.png').resize((194,240)))
        self.imSM = tk.Label(self.root, image = StartStarMap, bg = '#000000')
        self.imSM.place(relx = 0.75, rely = 0.29+0.16, relwidth = 0.24, relheight = 0.25)

        StartLP = ImageTk.PhotoImage(Image.open('assets/images/MTP-Model.png').resize((194,240)))
        self.imLP = tk.Label(self.root, image = StartLP, bg = '#000000')
        self.imLP.place(relx = 0.75, rely = 0.56+0.16, relwidth = 0.24, relheight = 0.25)
        
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.mainloop()

    def exit(self,*args):
        try: self.socket.close()
        except: pass
        self.root.destroy()

    def setconfigww(self):
        def setCnf():
            f = open('assets/config/config.txt', 'w')
            f.write(LE_var.get()+','+SM_var.get()+','+LP_var.get())
            f.close(); self.setconfigww.destroy()
            
        self.setconfigww = tk.Toplevel(self.root, bg='#000000')
        self.setconfigww.title('Set configuration')
        self.setconfigww.minsize(600,300)
        self.setconfigww.maxsize(600,300)
        self.setconfigww.focus_set()
        self.setconfigww.grab_set()
        self.setconfigww.transient(master=self.root)

        titlefont = tkFont.Font(family="Times New Roman", size=12)
        TLE = tk.Label(self.setconfigww, text = 'LONG EXPOSURE', bg='#000000', fg='#EE4C0F', font = titlefont)
        TSM = tk.Label(self.setconfigww, text = 'SKY MAP IMAGE SIZE', bg='#000000', fg='#EE4C0F', font = titlefont)
        TLP = tk.Label(self.setconfigww, text = 'LAPLACIAN FOR FOCUS', bg='#000000', fg='#EE4C0F', font = titlefont)

        TLE.place(relx = 0.012, rely = 0.02)
        TSM.place(relx = 0.333, rely = 0.02)
        TLP.place(relx = 0.680, rely = 0.02)
        
        LE_LAB = tk.Label(self.setconfigww, text = 'Number of frames', bg='#000000', fg='#04068E')
        SM_LAB = tk.Label(self.setconfigww, text = 'Full image pixel size', bg='#000000', fg='#04068E')
        LP_LAB = tk.Label(self.setconfigww, text = 'Order of filter', bg='#000000', fg='#04068E')

        LE_LAB.place(relx = 0.042, rely = 0.13)
        SM_LAB.place(relx = 0.393, rely = 0.13)
        LP_LAB.place(relx = 0.775, rely = 0.13)

        LE_var,SM_var,LP_var = tk.StringVar(),tk.StringVar(),tk.StringVar()
        LE = tk.Entry(self.setconfigww, textvariable = LE_var, bg='#2C2C2C', fg='#DB0E0E', bd = 0)
        SM = tk.Entry(self.setconfigww, textvariable = SM_var, bg='#2C2C2C', fg='#DB0E0E', bd = 0)
        LP = tk.Entry(self.setconfigww, textvariable = LP_var, bg='#2C2C2C', fg='#DB0E0E', bd = 0)

        LE.place(relx = 0.02, rely = 0.21, relwidth = 0.211)
        SM.place(relx = 0.34, rely = 0.21, relwidth = 0.265)
        LP.place(relx = 0.69, rely = 0.21, relwidth = 0.291)


        setConfig = tk.Button(self.setconfigww, text = 'Set configuration', command = setCnf)
        setConfig.place(relx = 0.375, rely = 0.9, relwidth = 0.25)

    def writeStarCoor(self):
        self.StarCoor.delete('1.0','end')
        self.StarCoorText = 'DEC: '+str(self.DEC)+'\nALT: '+str(self.ALT)+'\nAR: '+str(self.AR)+'\nAZ: '+str(self.AZ)
        self.StarCoor.insert('1.0',self.StarCoorText)

    def bPTF(self, event):
        self.pressed=True
        self.origenx=event.x
        self.origeny=event.y

    def mmTF(self, event):
        if(self.pressed and self.Mode_var.get() == 'Manual'):
            if(event.x >= 4 and event.x <= 139):
                self.TFC.delete("all")
                self.TFC.create_rectangle(0,0,event.x,40, width = 5,fill='#000445')
                if(event.x/139 == 1): self.TFC.create_text(70,18,fill='#C70039',font="Times 10 italic bold",text='Tuning focus '+str(int(event.x/139))); self.TF = '{:.3f}'.format(event.x/139); self.DataT0R('TF')
                elif((event.x-4)/139 == 0): self.TFC.create_text(70,18,fill='#C70039',font="Times 10 italic bold",text='Tuning focus '+str(int((event.x-4)/139))); self.TF = '{:.3f}'.format((event.x-4)/139); self.DataT0R('TF')
                else: self.TFC.create_text(70,18,fill='#C70039',font="Times 10 italic bold",text='Tuning focus '+'{:.3f}'.format(event.x/144)); self.TF = '{:.3f}'.format(event.x/144); self.DataT0R('TF')

    def mmFTF(self,event):
        if(self.pressed and self.Mode_var.get() == 'Manual'):
            if(event.x >= 4 and event.x <= 142):
                self.FTFC.delete("all")
                self.FTFC.create_rectangle(0,0,event.x,40, width = 5,fill='#000445')
                if(event.x/142 == 1): self.FTFC.create_text(72,18,fill='#C70039',font="Times 10 italic bold",text='Fine tuning focus '+str(int(event.x/142))); self.FTF = '{:.3f}'.format(event.x/142); self.DataT0R('FTF')
                elif((event.x-4)/142 == 0): self.FTFC.create_text(72,18,fill='#C70039',font="Times 10 italic bold",text='Fine tuning focus '+str(int((event.x-4)/142))); self.FTF = '{:.3f}'.format((event.x-4)/142); self.DataT0R('FTF')
                else: self.FTFC.create_text(73,18,fill='#C70039',font="Times 10 italic bold",text='Fine tuning focus '+'{:.3f}'.format(event.x/143)); self.FTF = '{:.3f}'.format(event.x/143); self.DataT0R('FTF')

    def bLeaveF(self,event):
        self.pressed=False

    def B1_Pressed(self, event):
        self.B1pressed=True
        self.origenx=event.x
        self.origeny=event.y
        self.By = event.y

    def B3_Pressed(self, event):
        self.B2pressed=True
        self.origenx=event.x
        self.origeny=event.y
        self.Bx = event.x

    def ALTInc(self, *args):
        if(self.ModeTogle == 1):
            self.ALT += 1
            if(self.ALT > 90): self.ALT = 90
            self.writeStarCoor()
            self.DataT0R('ALT')
            
    def ALTDec(self, *args):
        if(self.ModeTogle == 1):
            self.ALT -= 1
            if(self.ALT < 0): self.ALT = 0
            self.writeStarCoor()
            self.DataT0R('ALT')
        
    def AZInc(self, *args):
        if(self.ModeTogle == 1):
            self.AZ -= 1
            if(self.AZ < 0): self.AZ = 0
            self.writeStarCoor()
            self.DataT0R('AZ')
        
    def AZDec(self, *args):
        if(self.ModeTogle == 1):
            self.AZ += 1
            if(self.AZ > 360): self.AZ = 360
            self.writeStarCoor()
            self.DataT0R('AZ')

    def ModeE(self, *args):
        self.ModeTogle += 1
        if(self.ModeTogle > 1): self.ModeTogle = 0
        if(self.ModeTogle == 0): self.Mode_var.set('Auto'); self.Mode.config(bg = '#2A900A', fg = '#000000')
        if(self.ModeTogle == 1): self.Mode_var.set('Manual'); self.Mode.config(bg = '#B70707', fg = '#FFFFFF')

    def move_mouse(self, event):
        if(self.ModeTogle == 1):
            if self.B1pressed:
                self.canvas.create_line(self.origenx,self.origeny,event.x,event.y, fill="red")
                self.origenx=event.x
                self.origeny=event.y
                if(event.y < self.By):
                    self.ALT += 1
                    if(self.ALT > 90): self.ALT = 90
                if(event.y > self.By):
                    self.ALT -= 1
                    if(self.ALT < 0): self.ALT = 0
                self.writeStarCoor()
                self.DataT0R('ALT')
            if self.B2pressed:
                self.canvas.create_line(self.origenx,self.origeny,event.x,event.y, fill="green")
                self.origenx=event.x
                self.origeny=event.y
                if(event.x > self.Bx):
                    self.AZ += 1
                    if(self.AZ > 360): self.AZ = 360
                if(event.x < self.Bx):
                    self.AZ -= 1
                    if(self.AZ < 0): self.AZ = 0
                self.writeStarCoor()
                self.DataT0R('AZ')
    
    def botton_leave(self,event):
        self.B1pressed=False
        self.B2pressed=False
        self.Bx,self.By = 0,0
        self.canvas.delete("all")
        self.canvas.create_image(146, 100, image=self.background_image)
        
    def ImageRx(self):
        """ image receive from socket zmq """
        try:
            self.socket.send(b'1')
            message = self.socket.recv()
        except: self.imL.after(1,self.ImageRx)
        """ ----------------------------- """
        
        if(message != b'01E'):
            try:
                """                  Imge build                  """
                imData = base64.b64decode(message)
                imformat2np = np.frombuffer(imData, dtype=np.uint8)
                frame = cv2.imdecode(imformat2np, flags=1)
                frame = cv2.resize(frame,(680,420))
                """ -------------------------------------------- """
                
                """ Image acondicionate to PIL format """
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                """ --------------------------------- """    
                
                """ Image show in tk.Label """
                self.imL.imgtk = imgtk
                self.imL.configure(image=imgtk)
                self.imL.after(1,self.ImageRx)
            except: self.imL.after(1,self.ImageRx)
        else: print('end')

    def DataT0R(self, Data):
        if(Data == 'ALT'): self.sockZMQCLI.send_string('ALT'+str(self.ALT))
        elif(Data == 'FTF'): self.sockZMQCLI.send_string('FTF'+self.FTF)
        elif(Data == 'AZ'): self.sockZMQCLI.send_string('AZ'+str(self.AZ))
        elif(Data == 'TF'): self.sockZMQCLI.send_string('TF'+self.TF)
        data = self.sockZMQCLI.recv()

if __name__ == '__main__': MTPrx()
