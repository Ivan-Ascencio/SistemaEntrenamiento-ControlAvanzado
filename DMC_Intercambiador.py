from control import *
from control.matlab import c2d
import matplotlib.pyplot as plt
import wx
import os
import matplotlib
import random
import csv
import time
import threading
import queue
import random
import sys
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from numpy import sin,cos,tan,log,sqrt,exp,linspace

import subprocess
import SistemaEntrenamiento

cola=queue.LifoQueue()
matplotlib.use('WXAgg')

#----- Planta continua ----------------
#
#          1.7*e^(-8.4s)
#      ------------------
#       56.12s^2  + 15s +1 

#----- Planta discreta ----------------
#
#                  0.01043
#      ------------------------------------
#       (z+11) - 1.827*(z+10) + 0.8343(z+9)


numd =[0.0143]                           
dend = [1, -1.827, 0.8343,0,0,0,0,0,0,0,0,0]               
#Retardo del sistema
sistemad = tf(numd,dend)            #FT

#----- Planta discreta ----------------
Ts=0.5
[B,A] = tfdata(sistemad) #FT separado en num,den
plantadis = tf(sistemad)

#-------- Vector de coeficientes Gi  ---------------------
v=np.arange(0,30,0.5)
t1,y=step_response(sistemad,v) 
datadgi=y # gi: contiene la respuesta al escalón

M_maximo=len(datadgi)-1 #Horizonte de Prediccion del modelo Maximo 
gi=datadgi[0:len(datadgi)]  # coeficientes de la respuesta a escalon'''      



#---- Voy cambiando CONTROL LIBRE  despues de K+1 (k=P)
#duf=zeros(1,M_maximo);    %es el valor maximo
#M=8
#duf=np.zeros((1,M))
#duf=duf.transpose()    #delta de U : control libre 

#f_data=open(r"D:\data.txt","w",newline='')
#writer=csv.writer(f_data)
#writer.writerow(["n","t","y","u"])


class Timer1:
        
    def __init__(self,Tm,P,queue1): # que es queue1
        
        global det_muestreo
        det_muestreo=0

        self.periodo=0.5
        
        self.i=0
        self.cola=queue1
        self.u_act=0
        self.ta=time.time() 
        
        self.u=0
        self.u_ant1 =0
        self.u_ant2 =0
        self.u_ant3 =0
        self.u_ant4 =0
        self.u_ant5 =0
        self.u_ant6 =0
        self.u_ant7 =0
        self.u_ant8 =0
        self.u_ant9 =0
        self.u_ant10 =0
        self.u_ant11 =0
        
        self.ym=25
        self.ym_ant1 =25
        self.ym_ant2 =25

        self.yxm=25
        self.yxm_ant1 =25
        self.yxm_ant2 =25
        
        self.e_ant11=0
        self.e_ant10=0
        self.e_ant9=0
        self.e_ant8=0
        self.e_ant7=0
        self.e_ant6=0
        self.e_ant5=0
        self.e_ant4=0
        self.e_ant3=0
        self.e_ant2=0
        self.e_ant1=0
        self.e_act=0
    
                #Horizonte de prediccion 
        #self.N = 5            #Horizonte de control 
        self.Matriz_Gt1=np.matrix(gi[0:Pred])
        self.Matriz_Gt1=self.Matriz_Gt1.transpose()
        self.T=len(self.Matriz_Gt1) 
        self.G=[]
        

        for self.a in range(0,N) :

            self.C=np.zeros((self.a+1,1))
            self.D=np.matrix(self.Matriz_Gt1[1:self.T-self.a])
            self.arreglo=np.concatenate((self.C,self.D))
            self.G.append(self.arreglo)

        self.G = np.squeeze(np.asarray(self.G))
        self.G=self.G.transpose()

        self.Matriz_K = np.dot(np.dot(np.linalg.inv(np.dot(np.dot(self.G.transpose(),delta),self.G) + 
        np.dot(lamda,np.eye(N))),self.G.transpose()),delta)

        self.Kc = self.Matriz_K[0][:]

        self.duf=np.zeros((1,M))
        self.duf=self.duf.transpose() 

        w=0        #puedo colocar referencias futuras, hasta w=P
        self.B=np.squeeze(np.asarray(B))
        self.A=np.squeeze(np.asarray(A))       #puedo colocar referencias futuras, hasta w=P
        
        self.ym=np.matrix([25]) 
        self.ym=np.concatenate((self.ym,(np.full((15,1),25)))) 
        

    def actualizar(self):

        global ta,writer,SP, CV, PV, delta, lamda,P,tau, Ruido 

        self.i=self.i+1 
        tn=time.time()-self.ta 

        if tn>250:

                SP=35

        if tn>500:

                SP=45

        if tn>750:

                SP=35

        if tn>1000:

                SP=45

        self.ref = np.full((Pred,1),SP)

        if det_muestreo==0:
                self.timer1 = threading.Timer(self.periodo,self.actualizar) 
                self.timer1.start()

        
        self.f=np.matrix([])
        self.f=self.f.transpose()

        self.yxm=self.B*self.u_ant11 - self.A[1]*self.ym_ant1 - self.A[2]*self.ym_ant2 + Ruido*random.randint(-2, 2)
        self.ym=self.B*self.u_ant1 - self.A[1]*self.ym_ant1 - self.A[2]*self.ym_ant2

        for kk in range(0,Pred):
                                #KK pasados desde y(t), horizonte de prediccion
                self.vect_g=np.matrix([0]) 
                                #vector con las gkk+i - gkk
                for j in range(0,M):
                        Ma=np.matrix(gi[kk+j]-gi[j])
                        self.vect_g=np.concatenate((Ma,self.vect_g))    # gi(KK+1) = P a  M  %gi = 1 a P

                self.vect_g=self.vect_g[0:M]
                self.vect_g=self.vect_g.transpose()
                
                self.H=np.dot(self.vect_g,self.duf) 
                self.f=np.concatenate((self.ym+self.H,self.f))
                
        self.Vu_act =  self.Kc*(self.ref-self.f)
        self.u=self.u + self.Vu_act
        self.desplaza  = self.duf[1:M]
        self.duf = np.concatenate((self.Vu_act,self.desplaza))
        
        if self.yxm<25: 

                self.yf=25 
        
        if self.yxm>=25: 

                self.yf=self.yxm 
        
        self.e_ant11=self.e_ant10
        self.e_ant10=self.e_ant9
        self.e_ant9=self.e_ant8
        self.e_ant8=self.e_ant7
        self.e_ant7=self.e_ant6
        self.e_ant6=self.e_ant5
        self.e_ant5=self.e_ant4
        self.e_ant4=self.e_ant3
        self.e_ant3=self.e_ant2
        self.e_ant2=self.e_ant1
        self.e_ant1=self.e_act
        self.e_act=SP-self.ym #varia ym, yxm si se utiliza predictor smith

        self.u_ant11=self.u_ant10
        self.u_ant10=self.u_ant9
        self.u_ant9=self.u_ant8
        self.u_ant8=self.u_ant7
        self.u_ant7=self.u_ant6
        self.u_ant6=self.u_ant5
        self.u_ant5=self.u_ant4
        self.u_ant4=self.u_ant3
        self.u_ant3=self.u_ant2
        self.u_ant2=self.u_ant1
        self.u_ant1=self.u_ant1
        self.u_ant1=self.u
                
        self.ym_ant2=self.ym_ant1
        self.ym_ant1=self.ym_ant1
        self.ym_ant1=self.ym #varia ym, yxm si se utiliza predictor smith
                

        self.cola.put([float(self.yf),float(self.u)]) 
        print(self.i,tn,float(self.yf),float(self.u))
        #writer.writerow([self.i,tn,self.ym,self.u]) 

class FrameDMC(wx.Frame):
       

        def __init__(self,parent,title,cola1):

                wx.Frame.__init__(self,parent,title=title, pos=(1,1))
                self.pcanvas = wx.Panel(self,-1)
                self.pctrls = wx.Panel(self,-1)

                self.cola=cola1
                self.tiempo = 0
                self.ultimaT = 0
                self.TemperaturaD = 0

                # Sizers
                self.szmain = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)

                # Cuadros internos al principal
                self.szcanvas = wx.BoxSizer(wx.VERTICAL)
                self.szctrls = wx.FlexGridSizer(rows=6, cols=8, vgap=10, hgap=10)
                
                #se define las funciones canvas, controles y menu 
                self.initCanvas()
                self.initCtrls()
                self.initMenu()
                
                self.pcanvas.SetSizer(self.szcanvas) 
                self.pctrls.SetSizer(self.szctrls) 
                
                self.szmain.Add(self.pcanvas, 1, wx.EXPAND)
                self.szmain.Add(self.pctrls, 1, wx.EXPAND)
                
                self.SetSizer(self.szmain)
                
                self.intervalo = [0.0,10.0]
                self.xlabel = "Tiempo(S)"
                self.ylabel = "% Temperatura (°C)"
                self.Fit()
                #self.Centre(True)
                self.timer2 = wx.Timer(self)

                #Definir funcion asociada a timer
                self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer2)

        def OnTimer(self, event):
                self.tiempo = self.tiempo + Ts 

                y,u=self.cola.get() 
                
                #Dibujar punto
                self.axes.plot([self.tiempo,self.tiempo],[y,y], lw = 1, color='blue', marker='o', mfc = 'blue', mec = 'blue',  markersize = 2, label= 'Temperatura Sensada (PV)')
                self.axes.plot([self.tiempo],[u], lw = 1, color='green', marker='o', mfc = 'green', mec = 'green',  markersize = 2, label= 'Variable de Control (CV)') # Gráfica
                self.axes.plot([self.tiempo],[SP], lw = 1, color='red', marker='o', mfc = 'red', mec = 'red',  markersize = 2, label='Temperatura Deseada (SP)') # Gráfica

                if self.tiempo<=0.5:
                        self.axes.legend(loc='lower right',fontsize='12')
               

                self.axes.grid(True) # Coloca rejilla
                self.canvas.draw() # Redibuja el elementos "canvas"
                
                self.txtPV.SetValue(str(y))
                self.txtCV.SetValue(str(u))
                
        def initCanvas(self):
                # Creamos Figure
                self.figure = Figure(figsize=(16, 5), dpi=100)
                self.axes = self.figure.add_subplot(111)
                
                # FigureCanvas
                self.canvas = FigureCanvas(self.pcanvas, -1, self.figure)
                self.szcanvas.Add(self.canvas, 1, wx.EXPAND)
                
                
        def initCtrls(self):

                self.labelSP = wx.StaticText(self.pctrls, -1, "% Temp. Desada (SP):", size=(210, 25))                
                self.txtSP= wx.TextCtrl(self.pctrls, -1)

                self.labelPV = wx.StaticText(self.pctrls, -1, "% Temp. Sensada (PV):", size=(210, 25))
                self.txtPV = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelCV = wx.StaticText(self.pctrls, -1, "% Variable de Control (CV):", size=(210, 25))
                self.txtCV = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelDelta = wx.StaticText(self.pctrls, -1, "Delta :", size=(210, 25))                
                self.txtDelta = wx.TextCtrl(self.pctrls, -1)

                self.labelLamda = wx.StaticText(self.pctrls, -1, "Lamda :", size=(210, 25))
                self.txtLamda = wx.TextCtrl(self.pctrls, -1)
                
                self.labelPred = wx.StaticText(self.pctrls, -1, "Horizonte de Prediccion (P):", size=(220, 25))
                self.txtPred = wx.TextCtrl(self.pctrls, -1)

                self.labelHC = wx.StaticText(self.pctrls, -1, "Horizonte de control (N):", size=(220, 25))
                self.txtHC = wx.TextCtrl(self.pctrls, -1)

                self.labelHM = wx.StaticText(self.pctrls, -1, "Horizonte de Modelo (M):", size=(220, 25))
                self.txtHM = wx.TextCtrl(self.pctrls, -1)

                self.labelRuido = wx.StaticText(self.pctrls, -1, "Ruido:", size=(220, 25))
                self.txtRuido = wx.TextCtrl(self.pctrls, -1)


                self.botStart = wx.Button(self.pctrls, -1, "Start", size=(80, 25))
                self.botStart.SetFont( wx.Font( 11, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Serif" ) )
                self.botStart.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
                self.botStart.SetBackgroundColour( wx.Colour( 0, 126, 128 )  )

                self.botStop = wx.Button(self.pctrls, -1, "Stop", size=(80, 25))
                self.botStop.SetFont( wx.Font( 11, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Serif" ) )
                self.botStop.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
                self.botStop.SetBackgroundColour(  wx.Colour( 0, 126, 128 ) )

                self.botBack = wx.Button(self.pctrls, -1, "Back", size=(80, 25))
                self.botBack.SetFont( wx.Font( 11, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Serif" ) )
                self.botBack.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
                self.botBack.SetBackgroundColour(  wx.Colour( 0, 126, 128 )  )
                # Fuente
                mod_font = self.labelSP.GetFont()
                mod_font.SetPointSize(12)
                mod_font.SetWeight(wx.BOLD)

                #Set Point
                self.labelSP.SetFont(mod_font)
                self.txtSP.SetFont(mod_font)
                self.txtSP.SetForegroundColour((100,100,255))

                #Temperatura Sensada
                self.labelPV.SetFont(mod_font)
                self.txtPV.SetFont(mod_font)
                self.txtPV.SetBackgroundColour((255,255,0))
                
                #Voltaje enviado a la valvula.
                self.labelCV.SetFont(mod_font)
                self.txtCV.SetFont(mod_font)
                self.txtCV.SetBackgroundColour((255,255,0))

                #Constante Proporcional
                self.labelDelta.SetFont(mod_font)
                self.txtDelta.SetFont(mod_font)
                self.txtDelta.SetForegroundColour((100,100,255))

                #Constante Proporcional
                self.labelLamda.SetFont(mod_font)
                self.txtLamda.SetFont(mod_font)
                self.txtLamda.SetForegroundColour((100,100,255))

                #Horizonte de Prediccion
                self.labelPred.SetFont(mod_font)
                self.txtPred.SetFont(mod_font)
                self.txtPred.SetForegroundColour((100,100,255))

                #Horizonte de Control
                self.labelHC.SetFont(mod_font)
                self.txtHC.SetFont(mod_font)
                self.txtHC.SetForegroundColour((100,100,255))

                #Horizonte de Modelo
                self.labelHM.SetFont(mod_font)
                self.txtHM.SetFont(mod_font)
                self.txtHM.SetForegroundColour((100,100,255))

                self.labelRuido.SetFont(mod_font)
                self.txtRuido.SetFont(mod_font)
                self.txtRuido.SetForegroundColour((100,100,255))

                
                
                self.Bind(wx.EVT_BUTTON, self.iniciar, self.botStart)
                self.Bind(wx.EVT_BUTTON, self.finalizar, self.botStop)
                self.Bind(wx.EVT_BUTTON, self.regresar, self.botBack)


                #Set Point
                self.szctrls.Add(self.labelSP, 1, wx.EXPAND)
                self.szctrls.Add(self.txtSP, 1, wx.EXPAND)

                #Constante Proporcional
                self.szctrls.Add(self.labelDelta, 1, wx.EXPAND)
                self.szctrls.Add(self.txtDelta, 1, wx.EXPAND)

                self.szctrls.Add(self.labelHC, 1, wx.EXPAND)
                self.szctrls.Add(self.txtHC, 1, wx.EXPAND)
                
                #Caudal Sensado
                self.szctrls.AddSpacer(1)   
                self.szctrls.AddSpacer(1)    
                self.szctrls.Add(self.labelPV, 1, wx.EXPAND)
                self.szctrls.Add(self.txtPV, 1, wx.EXPAND)

                #Constante Integral
                self.szctrls.Add(self.labelLamda, 1, wx.EXPAND)
                self.szctrls.Add(self.txtLamda, 1, wx.EXPAND)

                self.szctrls.Add(self.labelHM, 1, wx.EXPAND)
                self.szctrls.Add(self.txtHM, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)
              

                #Voltaje enviado a la valvula
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelCV, 1, wx.EXPAND)
                self.szctrls.Add(self.txtCV, 1, wx.EXPAND)

                #Constante Derivativa
                self.szctrls.Add(self.labelPred, 1, wx.EXPAND)
                self.szctrls.Add(self.txtPred, 1, wx.EXPAND)

                self.szctrls.Add(self.labelRuido, 1, wx.EXPAND)
                self.szctrls.Add(self.txtRuido, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                

                self.szctrls.Add(self.botStart, 1, wx.ALL|wx.ALIGN_CENTER)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botStop, 1, wx.ALL|wx.ALIGN_CENTER)     
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botBack, 1, wx.ALL|wx.ALIGN_CENTER)     

               
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
        
        def isValid1(self,txtCtrl: wx.TextCtrl):
                valor = txtCtrl.GetValue()

                # Verificar si es número entero
                if not valor.isdigit():
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números enteros positivos", "Error", wx.OK | wx.ICON_ERROR)
                    return False

                numero = int(valor)

                # Validar rango
                if numero < 35 or numero > 45:
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("El valor debe estar entre 35 y 45", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                else:
                   txtCtrl.SetBackgroundColour(wx.NullColour)
                   txtCtrl.Refresh()
                   return True
                
        def isValid2(self,txtCtrl: wx.TextCtrl):
                valor = txtCtrl.GetValue()

                # Verificar si es número entero
                if not valor.isdigit():
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números enteros positivos", "Error", wx.OK | wx.ICON_ERROR)
                    return False

                numero = int(valor)

                # Validar rango
                if numero < 1 or numero > 1:
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("El valor debe ser 1", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                else:
                   txtCtrl.SetBackgroundColour(wx.NullColour)
                   txtCtrl.Refresh()
                   return True

        def isValid3(self,txtCtrl: wx.TextCtrl):
                valor = txtCtrl.GetValue()

                # Verificar si es número entero
                if not valor.isdigit():
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números enteros positivos", "Error", wx.OK | wx.ICON_ERROR)
                    return False

                numero = int(valor)

                # Validar rango
                if numero < 1 or numero > 28:
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("El valor debe estar entre 1 y 28", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                else:
                   txtCtrl.SetBackgroundColour(wx.NullColour)
                   txtCtrl.Refresh()
                   return True
                
        def isValid4(self,txtCtrl: wx.TextCtrl):
                valor = txtCtrl.GetValue()

                # Verificar si es número entero
                if not valor.isdigit():
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números enteros positivos", "Error", wx.OK | wx.ICON_ERROR)
                    return False

                numero = int(valor)

                # Validar rango
                if numero < 5 or numero > 24:
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("El valor debe estar entre 5 y 24", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                else:
                   txtCtrl.SetBackgroundColour(wx.NullColour)
                   txtCtrl.Refresh()
                   return True

        def isValid5(self,txtCtrl: wx.TextCtrl):
                valor = txtCtrl.GetValue()

                # Verificar si es número entero
                if not valor.isdigit():
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números enteros positivos", "Error", wx.OK | wx.ICON_ERROR)
                    return False

                numero = int(valor)

                # Validar rango
                if numero < 5 or numero > 24:
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("El valor debe estar entre 5 y 24", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                else:
                   txtCtrl.SetBackgroundColour(wx.NullColour)
                   txtCtrl.Refresh()
                   return True
                
        def isValid6(self,txtCtrl: wx.TextCtrl):
                valor = txtCtrl.GetValue()

                # Verificar si es número entero
                if not valor.isdigit():
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números enteros", "Error", wx.OK | wx.ICON_ERROR)
                    return False

                numero = int(valor)

                # Validar rango
                if numero < 5 or numero > 24:
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("El valor debe estar entre 5 y 24", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                else:
                   txtCtrl.SetBackgroundColour(wx.NullColour)
                   txtCtrl.Refresh()
                   return True

        def iniciar(self,event):
                if not self.isValid1(self.txtSP):
                        
                    return
                if not self.isValid2(self.txtDelta):
                    return
                if not self.isValid3(self.txtLamda):
                    return
                if not self.isValid4(self.txtPred):
                    return
                if not self.isValid5(self.txtHC):
                    return
                if not self.isValid6(self.txtHM):
                    return
                

                global SP,lamda,delta,Pred,op,M,N, Ruido

                self.timer2.Start(int(1000*Ts))
                self.tiempo = 0
                self.axes.cla()
                self.intervalo = [0.0,10.0]
                self.axes.set_title('Tiempo vs %Temperatura') # Configura título de la gráfica
                self.axes.set_xlabel(self.xlabel)
                self.axes.set_ylabel(self.ylabel)

                self.SP = float(self.txtSP.GetValue())
                self.delta = float(self.txtDelta.GetValue())
                self.lamda = float(self.txtLamda.GetValue())
                self.Pred= int(self.txtPred.GetValue())
                self.N= int(self.txtHC.GetValue())
                self.M= int(self.txtHM.GetValue())
                self.Ruido=float(self.txtRuido.GetValue())

                SP=self.SP
                delta=self.delta
                lamda=self.lamda
                Pred=self.Pred
                M=self.M
                N=self.N
                Ruido=self.Ruido

                if op==0: # ????
                        op=1 # ????
                        t1=Timer1(0.1,delta,self.cola) # ????
                        t1.actualizar() # ?????
                
        def finalizar(self,event):
                global det_muestreo
                self.timer2.Stop()
                det_muestreo=1
                
        def guardar(self,event):

                wldc = "PNG (*.png)|*.png"
                dlg=wx.FileDialog(self, "Guardar", os.getcwd(), style=wx.FD_SAVE | 
                                  wx.FD_OVERWRITE_PROMPT, wildcard=wldc)
                if dlg.ShowModal() == wx.ID_OK:
                        self.figure.savefig(dlg.GetPath())
                dlg.Destroy()

        def regresar(self,event):
                global f_data
                global det_muestreo
                self.timer2.Stop()
                det_muestreo=1
                subprocess.Popen(['python3' , 'SistemaEntrenamiento.py'])
                sys.exit(FrameDMC)
                f_data.close()
               

        def salir(self,event):
                global f_data
                self.Close(True)
                f_data.close()


if __name__=='__main__':

        op=0
        print("sip")

        app = wx.App()
        frame = FrameDMC(None,"Graficador",cola)
        frame.Show()
        app.MainLoop()