import wx
import os
import matplotlib
import random
import csv
import time
import threading
import queue
from control import *
from control.matlab import c2d


import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from numpy import sin,cos,tan,log,sqrt,exp,linspace

import subprocess
import sys
from collections import deque

cola1=queue.LifoQueue()
cola2=queue.LifoQueue()

matplotlib.use('WXAgg')

# CSV
#f_data=open(r"C:\Users\IVAN\Desktop\TESIS MSc\Codigos Python PUCP\data.txt","w",newline='')
#f_data=open(r"C:\Users\ivana\Desktop\GP_Tesis\data.txt","w",newline='')

#writer=csv.writer(f_data)
#writer.writerow(["n","t","y","u"])
        

#Tiempo de muestreo
Ts=0.5 #segundos (para el ploteo)
KC=1

class Timer1:
        
    def __init__(self,Tm,P,queue1,queue2): # que es queue1
        
        global det_muestreo
        det_muestreo=0

        self.periodo=0.5
        
        self.i=0
        self.cola1=queue1
        self.cola2=queue2
        self.ta=time.time()

        self.u_hist = deque([0.0]*181, maxlen=181)   # u_ant1 .. u_ant180
        self.up_hist = deque([0.0]*216, maxlen=216) # up_ant1 .. up_ant215

      
        self.u_act=0

       
        self.up_act=0
        
        self.Yn_ant1 =20
        self.Yn=20
        self.YXn_ant1=20
        self.YXn=20

        self.Pn_ant1=14.5
        self.Pn=14.5
        self.PXn_ant1=14.5
        self.PXn=14.5
  
        e_act=0
        self.e_ant=0
        self.e_ant1=0
        self.e_ant2=0
        self.e_ant3=0
        
        ep_act=0
        self.ep_ant1=0
        self.ep_ant2=0

        self.SP1=20
        self.SP3=14.5
        

    def actualizar(self):

        global ta,writer,SP, CV, PV,K, Kp, Ki, Kd, K2 , Kp2, Kp2, Ki2, tau, tau2,Kp1,Ki1 #?
     
        self.i=self.i+1 
        tn=time.time()-self.ta
          
        # configurando el setpoint de la temperatura de la autoclave 

        if self.SP1<SP:
                
                self.SP1=self.SP1+0.05

        if self.SP1>=SP:

                self.SP1=SP

        # configurando el setpoint de la presion de la autoclave

        SP2=0.25*(SP-100)+25
        
        if self.Yn<80:

                self.SP3=14.5

        if self.Yn>=80:

                self.SP3=SP2

        #realizando el seteo de las ganancias programadas

        if SP<=100 and SP2<=25:

                self.Esc=50
                self.K=3.57
                self.tau=321.4
                self.K2=0.94
                self.tau2=754.3

                #retardo del sistema
                self.u_ret=self.u_hist[65]  #self.u_ant66
                self.up_ret=self.up_hist[99]
                
                #controlador de temperatura
                Kp=42.6
                Ki=0.7977
                Kd=0
        
                #controlador de presion
                Kp2=389.05
                Ki2=3.7185
                Kd2=0

        if SP>100 and SP<=110 and SP2>25 and SP2<=27.5:

                self.Esc=55
                self.K=0.96
                self.tau=289.9
                self.K2=0.93
                self.tau2=300

                #retardo del sistema
                self.u_ret=self.u_hist[117]
                self.up_ret=self.up_hist[75]

                #controlador de temperatura
                Kp=144.54
                Ki=1.1796
                Kd=0

                #controlador de presion
                Kp2=154.88
                Ki2=7.79
                Kd2=0
                
        if SP>110 and SP<=120 and SP2>27.5 and SP2<=30:

                self.Esc=60
                self.K=1.04
                self.tau=367.5
                self.K2=1.427
                self.tau2=288.7
                
                #retardo del sistema
                self.u_ret=self.u_hist[124]
                self.up_ret=self.up_hist[163]

                Kp=169.8243
                Ki=1.8928
                Kd=0

                Kp2=96.605
                Ki2=1.5263
                Kd2=0

        if SP>120 and SP<=130 and SP2>30 and SP2<=32.5:
                
                self.Esc=65
                self.K=1.02
                self.tau=463.2
                self.K2=1.92
                self.tau2=441.4

                #retardo del sistema
                self.u_ret=self.u_hist[179] #self.u_ant180
                self.up_ret=self.up_hist[214] #self.up_ant215

                Kp=218.7761
                Ki=2.4941
                Kd=0 
                Kp2=110.9174
                Ki2=1.6970
                Kd2=0

        if SP>130 and SP<=140 and SP2>32.5 and SP2<=35:

                self.Esc=70
                self.K=0.58
                self.tau=249.6
                self.K2=1.56
                self.tau2=356.7
                        
                #retardo del sistema
                self.u_ret=self.u_hist[99] #u_ant100
                self.up_ret=self.up_hist[99] #up_ant100

                Kp=145.9854
                Ki=1.3826
                Kd=0
                Kp2=109.6478
                Ki2=1.0478
                Kd2=0

        if SP>140 and SP<=150  and SP2>35 and SP2<=37.5:

                self.Esc=75
                self.K=0.704
                self.tau=206.5
                self.K2=2.4
                self.tau2=198.1

                self.u_ret=self.u_hist[142] #self.u_ant143
                self.up_ret=self.up_hist[41]
               
                Kp=141.2538
                Ki=2.1612
                Kd=0
                Kp2=39.8107
                Ki2=0.6091
                Kd2=0

        
        #Planta de temperatura
        num=[self.K]
        den=[self.tau,1]
        planta = tf(num,den)
        sistemad = sample_system(planta,Ts)
        [B,A]=tfdata(sistemad)
        self.B=np.squeeze(np.asarray(B))
        self.A=np.squeeze(np.asarray(A))

        #Planta de presión
        num2=[self.K2]
        den2=[self.tau2,1]
        planta2 = tf(num2,den2)
        sistemad2 = sample_system(planta2,Ts)
        [D,C]=tfdata(sistemad2)
        self.D=np.squeeze(np.asarray(D))
        self.C=np.squeeze(np.asarray(C))

        #print(self.D)
        #print(self.C[0], self.C[1])

        if det_muestreo==0:
                self.timer1 = threading.Timer(self.periodo,self.actualizar) 
                self.timer1.start()

        ########################################################################################
        #Calculo de la Variable de Proceso despues de salir del proceso 
        #Planta G(s)=K/(tau*S+1)=3.543/(0.56*s+1)

        self.Yn=(self.B*self.u_ret - self.Yn_ant1*self.A[1])/self.A[0] #planta de temperatura
        self.YXn=(self.B*self.u_hist[0] - self.YXn_ant1*self.A[1])/self.A[0]

        self.Pn=(self.D*self.up_ret - self.Pn_ant1*self.C[1])/self.C[0] # planta de presión
        self.PXn=(self.D*self.up_hist[0] - self.PXn_ant1*self.C[1])/self.C[0]
        
        self.Yn_ant1=self.Yn 
        self.YXn_ant1=self.YXn
        e_act=self.SP1-self.YXn

        self.Pn_ant1=self.Pn 
        self.PXn_ant1=self.PXn
        ep_act=self.SP3-self.PXn

        #self.Yn=self.Yn*27.03-27.03 # escalando la señal del transmisor

        
        #########################################################################################
        #calculo del error actual
        #e_act=self.SP1-self.Yn
        #ep_act=self.SP3-self.Pn
       
        ##########################################################################################
        #Controlador PI para la planta de temperatura
        #Calculo de la Variable de Control CV, señal de exitacion de actuador
               
        Prop=(e_act- self.e_ant2)*Kp

        Int=(e_act + 2*self.e_ant1 + self.e_ant2)*(Ki*self.periodo)/2

        Der=(e_act - 2*self.e_ant1 + self.e_ant2)*(2*Kd/self.periodo)

        self.u_act= self.u_hist[1] + Prop + Int + Der

        if self.u_act<=100 and self.u_act>=0:

                self.u_act=self.u_act
        
        if self.u_act>100:

                self.u_act=100
        
        if self.u_act<0:

                self.u_act=0

        #Controlador PI para la planta de presión
        #Calculo de la Variable de Control CV, señal de exitacion de actuador

        Prop_P=(ep_act- self.ep_ant2)*Kp2

        Int_P=(ep_act + 2*self.ep_ant1 + self.ep_ant2)*(Ki2*self.periodo)/2

        Der_P=(ep_act - 2*self.ep_ant1 + self.ep_ant2)*(2*Kd2/self.periodo)

        self.up_act= self.up_hist[1]+ Prop_P + Int_P + Der_P

        #se truncara el valor de la señal de control:

        if self.up_act<=70 and self.up_act>=0:

                self.up_act=self.up_act
        
        if self.up_act>70:

                self.up_act=70

        if self.up_act<0:

                self.up_act=0

       

        ##########################################################################################
        self.u_hist.appendleft(self.u_act)
        self.up_hist.appendleft(self.up_act)

       # self.up_ant1=self.up_act

        self.e_ant2=self.e_ant1
        self.e_ant1=e_act

        self.ep_ant2=self.ep_ant1
        self.ep_ant1=ep_act
        

        #self.u_act=self.u_act*0.1 # escalando la señal del actuador, convirtiendola en voltios.

        ##########################################################################################
        self.cola1.put([self.Yn,self.u_act,self.Esc,e_act,self.SP1,Kp,Ki])
        self.cola2.put([self.Pn,self.up_act,self.Esc,ep_act,self.SP3,SP2,Kp2,Ki2])
        

        print(self.i,tn,self.Yn,self.u_act)
        print(self.i,tn,self.Pn,self.up_act)
        

        # Guardar fila 
        #writer.writerow([self.i,tn,self.Yn,self.u_act]) 
        
        
class GP_Autoclave(wx.Frame):

        def __init__(self,parent,title,cola1,cola2):

                wx.Frame.__init__(self,parent,title=title, pos=(1,1))
                self.pcanvas = wx.Panel(self,-1)
                self.pcanvas2= wx.Panel(self,-1)
                self.pctrls = wx.Panel(self,-1)
                self.pctrls2 = wx.Panel(self,-1)

                self.cola1=cola1
                self.cola2=cola2
                self.tiempo = 0
                self.ultimaT = 0
                self.TemperaturaD = 0

                # Sizers
                self.szmain = wx.FlexGridSizer(rows=2, cols=2, vgap=0, hgap=0) #GRAFICA
                #self.szmain2 = wx.FlexGridSizer(rows=1, cols=1, vgap=0, hgap=0) #CONTROLES

                # Cuadros internos al principal
                self.szcanvas = wx.BoxSizer(wx.HORIZONTAL)
                self.szcanvas2 = wx.BoxSizer(wx.HORIZONTAL)
                self.szctrls = wx.FlexGridSizer(rows=6, cols=7, vgap=10, hgap=10)
                self.szctrls2 = wx.FlexGridSizer(rows=6, cols=7, vgap=10, hgap=10)
                
                #se define las funciones canvas, controles y menu 
                self.initCanvas()
                self.initCtrls()
                self.initMenu()
                
                self.pcanvas.SetSizer(self.szcanvas) 
                self.pcanvas2.SetSizer(self.szcanvas2)
                self.pctrls.SetSizer(self.szctrls)
                self.pctrls2.SetSizer(self.szctrls2) 
                
                self.szmain.Add(self.pcanvas, 1, wx.EXPAND)
                self.szmain.Add(self.pcanvas2, 1, wx.EXPAND)
                self.szmain.Add(self.pctrls, 1, wx.EXPAND)
                self.szmain.Add(self.pctrls2, 1, wx.EXPAND)
                
                self.SetSizer(self.szmain)

                self.intervalo = [0.0,10.0]
                self.xlabel = "Tiempo(S)"
                self.ylabel = "% Temperatura Deseada (SP)\n\n% Temperatura Sensada (PV)\n\n Variable de Control (V)"
                self.xlabel2 = "Tiempo(S)"
                self.ylabel2 = "% Presion Deseada (SP)\n\n% Presion Sensada (PV)\n\n Variable de Control (V)"

                self.Fit()
                #self.center(True)
                self.timer2 = wx.Timer(self)

                #Definir funcion asociada a timer
                self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer2)

        def OnTimer(self, event):
                self.tiempo = self.tiempo + Ts 

                [y,u,Esc,e_act,SP1,Kp1,Ki1]=self.cola1.get() 
                [Pn,up,Escp,ep_act,SP3,SP2,Kp2,Ki2]=self.cola2.get()

                #[y,u]=self.cola.get() 
                
                #Dibujar punto
                self.axes.plot([self.tiempo,self.tiempo],[y,y], lw = 1, color='blue', marker='o', mfc = 'blue', mec = 'blue',  markersize = 1, label= 'Temperatura Sensada (TPV)') # Gráfica
                self.axes.plot([self.tiempo],[u], lw = 1, color='green', marker='o', mfc = 'green', mec = 'green',  markersize = 1, label= 'Variable de Control (CV)') # Gráfica
                self.axes.plot([self.tiempo],[SP1], lw = 1, color='red', marker='o', mfc = 'red', mec = 'red',  markersize = 1,label='Temperatura Deseada (SP)') # Gráfica
                
                '''self.axes.plot([self.tiempo,self.tiempo],[y,y], lw = 1, color='green', marker='o', mfc = 'green', mec = 'green',  markersize = 1, label= '% Apertura Valvula') # Gráfica
                self.axes.plot([self.tiempo],[u], lw = 1, color='blue', marker='o', mfc = 'blue', mec = 'blue',  markersize = 1, label= '% Caudal Medido') # Gráfica
                self.axes.plot([self.tiempo],[SP1], lw = 1, color='blue', marker='o', mfc = 'blue', mec = 'blue',  markersize = 1) # Gráfica'''

                if self.tiempo<=0.5:
                        self.axes.legend(loc='upper left',fontsize='12')

                self.axes.grid(True) # Coloca rejilla
                self.canvas.draw() # Redibuja el elementos "canvas"
                
                self.axes2.plot([self.tiempo,self.tiempo],[Pn,Pn], lw = 1, color='blue', marker='o', mfc = 'blue', mec = 'blue',  markersize = 1, label= 'Presion Sensada (PPV)') # Gráfica
                self.axes2.plot([self.tiempo],[up], lw = 1, color='green', marker='o', mfc = 'green', mec = 'green',  markersize = 1, label= 'Variable de Control (CV)') # Grafica
                self.axes2.plot([self.tiempo],[SP3], lw = 1, color='red', marker='o', mfc = 'red', mec = 'red',  markersize = 1,label='Presion Deseada (SP)') # Gráfica
                
                '''self.axes2.plot([self.tiempo,self.tiempo],[Pn,Pn], lw = 1, color='green', marker='o', mfc = 'green', mec = 'green',  markersize = 1, label= 'Presion Sensada (PPV)') # Gráfica
                self.axes2.plot([self.tiempo],[up], lw = 1, color='orange', marker='o', mfc = 'orange', mec = 'orange',  markersize = 1, label= 'Variable de Control (CV)') # Grafica
                self.axes2.plot([self.tiempo],[SP3], lw = 1, color='blue', marker='o', mfc = 'blue', mec = 'blue',  markersize = 1, label='Presion Deseada (SP)') # Gráfica'''

                if self.tiempo<=0.5:
                        self.axes2.legend(loc='upper left',fontsize='12')
                
                self.axes2.grid(True)
                self.canvas2.draw() # Redibuja el elementos "canvas"
                
                self.txtTPV.SetValue(str(y))
                self.txtCV.SetValue(str(u))
                self.txtEsc.SetValue(str(Esc))
                self.txtE.SetValue(str(e_act))
                self.txtKp1.SetValue(str(Kp1))
                self.txtKi1.SetValue(str(Ki1))

                #self.txtPPV.SetValue(str(u))

                self.txtPPV2.SetValue(str(Pn))
                self.txtCV2.SetValue(str(up))
                self.txtEsc2.SetValue(str(Escp))
                self.txtE2.SetValue(str(ep_act))
                self.txtKp2.SetValue(str(Kp2))
                self.txtKi2.SetValue(str(Ki2))
                self.txtSP2.SetValue(str(SP2))
                
        def initCanvas(self):
                # Creamos Figure
                self.figure = Figure(figsize=(7.5, 5), dpi=100)
                self.figure2 = Figure(figsize=(7.5, 5), dpi=100)
                self.axes = self.figure.add_subplot(111)
                self.axes2 = self.figure2.add_subplot(111)
                
                # FigureCanvas
                self.canvas = FigureCanvas(self.pcanvas, -1, self.figure)
                self.canvas2 = FigureCanvas(self.pcanvas2, -1, self.figure2)
                self.szcanvas.Add(self.canvas, 1, wx.EXPAND)
                self.szcanvas2.Add(self.canvas2, 1, wx.EXPAND)
                
        def initCtrls(self):

                # primer cuadro de controles
                self.labelSP = wx.StaticText(self.pctrls, -1, "% Temperatura Des.(SP):", size=(210, 25))                
                self.txtSP= wx.TextCtrl(self.pctrls, -1)

                self.labelTPV = wx.StaticText(self.pctrls, -1, "% Temperatura Sens.(TPV):", size=(210, 25))
                self.txtTPV = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelEsc = wx.StaticText(self.pctrls, -1, " Escala(Esc) : ", size=(40, 25))                
                self.txtEsc = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelCV = wx.StaticText(self.pctrls, -1, "% Variable de Control (CV):", size=(210, 25))
                self.txtCV = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelE = wx.StaticText(self.pctrls, -1, "Error Actual (E):", size=(210, 25))
                self.txtE = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.botStart = wx.Button(self.pctrls, -1, "Start", size=(80, 25))
                self.botStart.SetFont( wx.Font( 11, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Serif" ) )
                self.botStart.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
                self.botStart.SetBackgroundColour( wx.Colour( 0, 126, 128 )  )

                self.botStop = wx.Button(self.pctrls, -1, "Stop", size=(80, 25))
                self.botStop.SetFont( wx.Font( 11, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Serif" ) )
                self.botStop.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
                self.botStop.SetBackgroundColour( wx.Colour( 0, 126, 128 )  )

                self.botBack = wx.Button(self.pctrls, -1, "Back", size=(80, 25))
                self.botBack.SetFont( wx.Font( 11, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Serif" ) )
                self.botBack.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
                self.botBack.SetBackgroundColour( wx.Colour( 0, 126, 128 )  )

                self.labelKp1 = wx.StaticText(self.pctrls, -1, "Const. Prop. 1 (Kp1):", size=(210, 25))
                self.txtKp1 = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelKi1 = wx.StaticText(self.pctrls, -1, "Const. Int. 1 (Ki1):", size=(210, 25))
                self.txtKi1 = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)
                
                #segundo cuadro de controles

                self.labelSP2 = wx.StaticText(self.pctrls2, -1, "% Presion Des.(SP):", size=(210, 25))                
                self.txtSP2= wx.TextCtrl(self.pctrls2, -1, '', style=wx.TE_READONLY)

                self.labelPPV2 = wx.StaticText(self.pctrls2, -1, "% Presion Sens.(PPV):", size=(210, 25))
                self.txtPPV2 = wx.TextCtrl(self.pctrls2, -1, '', style=wx.TE_READONLY)

                self.labelEsc2 = wx.StaticText(self.pctrls2, -1, " Escala(Esc) : ", size=(40, 25))                
                self.txtEsc2 = wx.TextCtrl(self.pctrls2, -1, '', style=wx.TE_READONLY)

                self.labelCV2 = wx.StaticText(self.pctrls2, -1, "% Variable de Control (CV):", size=(210, 25))
                self.txtCV2 = wx.TextCtrl(self.pctrls2, -1, '', style=wx.TE_READONLY)

                self.labelE2 = wx.StaticText(self.pctrls2, -1, "Error Actual (E):", size=(210, 25))
                self.txtE2 = wx.TextCtrl(self.pctrls2, -1, '', style=wx.TE_READONLY)

                self.labelKp2 = wx.StaticText(self.pctrls2, -1, "Const. Prop. 2 (Kp2):", size=(210, 25))
                self.txtKp2 = wx.TextCtrl(self.pctrls2, -1, '', style=wx.TE_READONLY)

                self.labelKi2 = wx.StaticText(self.pctrls2, -1, "Const. Int. 2 (Ki2):", size=(210, 25))
                self.txtKi2 = wx.TextCtrl(self.pctrls2, -1, '', style=wx.TE_READONLY)
                
                # Fuente
                mod_font = self.labelSP.GetFont()
                mod_font.SetPointSize(12)
                mod_font.SetWeight(wx.BOLD)

                #Set Point
                self.labelSP.SetFont(mod_font)
                self.txtSP.SetFont(mod_font)
                self.txtSP.SetForegroundColour((100,100,255))

                self.labelSP2.SetFont(mod_font)
                self.txtSP2.SetFont(mod_font)
                self.txtTPV.SetBackgroundColour((255,255,0))

                #Temperatura Sensada
                self.labelTPV.SetFont(mod_font)
                self.txtTPV.SetFont(mod_font)
                self.txtTPV.SetBackgroundColour((255,255,0))
                
                #Voltaje enviado a la valvula.
                self.labelPPV2.SetFont(mod_font)
                self.txtPPV2.SetFont(mod_font)
                self.txtPPV2.SetBackgroundColour((255,255,0))

                #Constante Proporcional
                self.labelCV.SetFont(mod_font)
                self.txtCV.SetFont(mod_font)
                self.txtCV.SetBackgroundColour((255,255,0))

                self.labelCV2.SetFont(mod_font)
                self.txtCV2.SetFont(mod_font)
                self.txtCV2.SetBackgroundColour((255,255,0))

                #Constante Proporcional
                self.labelEsc.SetFont(mod_font)
                self.txtEsc.SetFont(mod_font)
                self.txtEsc.SetBackgroundColour((255,255,0))

                self.labelEsc2.SetFont(mod_font)
                self.txtEsc2.SetFont(mod_font)
                self.txtEsc2.SetBackgroundColour((255,255,0))

                #Error
                self.labelE.SetFont(mod_font)
                self.txtE.SetFont(mod_font)
                self.txtE.SetBackgroundColour((255,255,0))

                self.labelE2.SetFont(mod_font)
                self.txtE2.SetFont(mod_font)
                self.txtE2.SetBackgroundColour((255,255,0))

                #constante proporcional
                self.labelKp1.SetFont(mod_font)
                self.txtKp1.SetFont(mod_font)
                self.txtKp1.SetBackgroundColour((255,255,0))

                self.labelKp2.SetFont(mod_font)
                self.txtKp2.SetFont(mod_font)
                self.txtKp2.SetBackgroundColour((255,255,0))

                #constante integral
                self.labelKi1.SetFont(mod_font)
                self.txtKi1.SetFont(mod_font)
                self.txtKi1.SetBackgroundColour((255,255,0))

                self.labelKi2.SetFont(mod_font)
                self.txtKi2.SetFont(mod_font)
                self.txtKi2.SetBackgroundColour((255,255,0))
                
                self.Bind(wx.EVT_BUTTON, self.iniciar, self.botStart)
                self.Bind(wx.EVT_BUTTON, self.finalizar, self.botStop)
                self.Bind(wx.EVT_BUTTON, self.regresar, self.botBack)

                #Set Point
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelSP, 1, wx.EXPAND)
                self.szctrls.Add(self.txtSP, 1, wx.EXPAND)

                #escala
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelEsc, 1, wx.EXPAND)
                self.szctrls.Add(self.txtEsc, 1, wx.EXPAND)
                
                #temeperatura Sensada
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelTPV, 1, wx.EXPAND)
                self.szctrls.Add(self.txtTPV, 1, wx.EXPAND)

                #variable de control
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelCV, 1, wx.EXPAND)
                self.szctrls.Add(self.txtCV, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)

                #error
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelE, 1, wx.EXPAND)
                self.szctrls.Add(self.txtE, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)

                #Constante porporcional 1
                self.szctrls.Add(self.labelKp1, 1, wx.EXPAND)
                self.szctrls.Add(self.txtKp1, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)

                #Constante integral 1
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelKi1, 1, wx.EXPAND)
                self.szctrls.Add(self.txtKi1, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                


                #boton star y stop
                self.szctrls.Add(self.botStart, 1, wx.ALL|wx.ALIGN_CENTER)
                self.szctrls.AddSpacer(1)

                self.szctrls.Add(self.botStop, 1, wx.ALL|wx.ALIGN_CENTER) 
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botBack, 1, wx.ALL|wx.ALIGN_CENTER)     
  
                self.szctrls.AddSpacer(1)
        
                #Set point Presion
                self.szctrls2.Add(self.labelSP2, 1, wx.EXPAND)
                self.szctrls2.Add(self.txtSP2, 1, wx.EXPAND)

                #escala 2
                self.szctrls2.AddSpacer(1)
                self.szctrls2.Add(self.labelEsc2, 1, wx.EXPAND)
                self.szctrls2.Add(self.txtEsc2, 1, wx.EXPAND)
                
                #variable de proceso
                self.szctrls2.AddSpacer(1)
                self.szctrls2.AddSpacer(1)
                self.szctrls2.Add(self.labelPPV2, 1, wx.EXPAND)
                self.szctrls2.Add(self.txtPPV2, 1, wx.EXPAND)

                #variable de control
                self.szctrls2.AddSpacer(1)
                self.szctrls2.Add(self.labelCV2, 1, wx.EXPAND)
                self.szctrls2.Add(self.txtCV2, 1, wx.EXPAND)
                self.szctrls2.AddSpacer(1)


                #error2 
                self.szctrls2.AddSpacer(1)
                self.szctrls2.Add(self.labelE2, 1, wx.EXPAND)
                self.szctrls2.Add(self.txtE2, 1, wx.EXPAND)
                self.szctrls2.AddSpacer(1)

                #Constante proporcional 2
                self.szctrls2.Add(self.labelKp2, 1, wx.EXPAND)
                self.szctrls2.Add(self.txtKp2, 1, wx.EXPAND)
                self.szctrls2.AddSpacer(1)

                #Constante integral 2
                self.szctrls2.AddSpacer(1)
                self.szctrls2.Add(self.labelKi2, 1, wx.EXPAND)
                self.szctrls2.Add(self.txtKi2, 1, wx.EXPAND)
                self.szctrls2.AddSpacer(1)
                
               
        def initMenu(self):
                m_archivo = wx.Menu()
                guardar = m_archivo.Append(-1, "Guardar")
                salir = m_archivo.Append(-1, "Salir")
                menu_bar = wx.MenuBar()
                menu_bar.Append(m_archivo, "Archivo")
                #menu_bar.Append(m_configurar, "Configurar")
                self.SetMenuBar(menu_bar)
                
                self.Bind(wx.EVT_MENU, self.guardar, guardar)
                self.Bind(wx.EVT_MENU, self.salir, salir)
               
        
        def isValid(self,txtCtrl: wx.TextCtrl):
                valor = txtCtrl.GetValue()

                # Verificar si es número entero
                if not valor.isdigit():
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números enteros positivos", "Error", wx.OK | wx.ICON_ERROR)
                    return False

                numero = int(valor)

                # Validar rango
                if numero < 100 or numero > 150:
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("El valor debe estar entre 100 y 150", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                else:
                   txtCtrl.SetBackgroundColour(wx.NullColour)
                   txtCtrl.Refresh()
                   return True

        def iniciar(self,event):

                if not self.isValid(self.txtSP):
                        
                    return
                global SP,SP2,Kp,Ki,Kd,K,op

                self.timer2.Start(int(1000*Ts))    # ???....._____0.2 second interval self.timer.start()
                self.tiempo = 0
                self.axes.cla()
                self.axes2.cla()
                self.intervalo = [0.0,10.0]
                self.axes.set_title('Tiempo vs %Temperatura') # Configurar título de la gráfica
                self.axes.set_xlabel(self.xlabel)
                self.axes.set_ylabel(self.ylabel)
                self.axes2.set_title('Tiempo vs %Presion') # Configurar título de la gráfica
                self.axes2.set_xlabel(self.xlabel2)
                self.axes2.set_ylabel(self.ylabel2)

                self.SP = float(self.txtSP.GetValue())
                #self.SP2 = float(self.txtSP2.GetValue())
                #self.KP = float(self.txtKP.GetValue())
                #self.KI = float(self.txtKI.GetValue())
                #self.KD = float(self.txtKD.GetValue())

                SP=self.SP
                #SP2=self.SP2
                #K=self.K
                #Ki=self.KI
                #Kd=self.KD

                if op==0: # ????
                        op=1 # ????
                        t1=Timer1(0.1,KC,self.cola1,self.cola2) # ????
                        t1.actualizar() # ?????
                
        def finalizar(self,event):
                global det_muestreo
                self.timer2.Stop()
                det_muestreo=1
                
        def guardar(self,event):

                wldc = "PNG (*.png)|*.png"
                dlg=wx.FileDialog(self, "Guardar", os.getcwd(), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=wldc)
                if dlg.ShowModal() == wx.ID_OK:
                        self.figure.savefig(dlg.GetPath())
                dlg.Destroy()
        
        def regresar(self,event):
                global f_data
                global det_muestreo
                self.timer2.Stop()
                det_muestreo=1
                subprocess.Popen(['python3' , 'SistemaEntrenamiento.py'])
                sys.exit(GP_Autoclave)
                f_data.close()
        
        def salir(self,event):
                global f_data
                self.Close(True)
                f_data.close()
                
                        
if __name__=='__main__':

        op=0
        print("sip")

        app = wx.App()
        frame = GP_Autoclave(None,"Graficador",cola1,cola2)
        frame.Show()
        app.MainLoop()

        