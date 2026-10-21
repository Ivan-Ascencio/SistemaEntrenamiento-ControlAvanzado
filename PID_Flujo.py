
import wx
import os
import matplotlib
import random
import csv
import time
import threading
import queue
import re
cola=queue.LifoQueue()
matplotlib.use('WXAgg')

import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from numpy import sin,cos,tan,log,sqrt,exp,linspace

# CSV
#f_data=open(r"C:\Users\IVAN\Desktop\TESIS MSc\Codigos Python PUCP\data.txt","w",newline='')
#f_data=open(r"C:\Users\ivana\Desktop\ControlPID_Tesis\data.txt","w",newline='')
#writer=csv.writer(f_data)
#writer.writerow(["n","t","y","u"])
        

#Tiempo de muestreo
Ts=0.5 #segundos (para el ploteo)



class Timer1:
        
    def __init__(self,Tm,P,queue1): # que es queue1
        
        global det_muestreo
        det_muestreo=0

        self.periodo=0.5
        
        self.i=0
        self.cola=queue1
        self.u_act=0
        self.ta=time.time()
        self.K=3.534 #ganancia de proceso
        self.Yn=0
        self.tau=0.56 #constante de tiempo.
        self.Yn_1=0

        self.e_ant2 =0
        self.e_ant  =0
        self.u_ant2 =0
        self.u_ant  =0
        

    def actualizar(self):

        global ta,writer,SP, CV, PV, Kp, Ki,Kd,tau #?
     
        self.i=self.i+1 #?
        tn=time.time()-self.ta #?

        if det_muestreo==0:
                self.timer = threading.Timer(self.periodo,self.actualizar) 
                self.timer.start()


        ########################################################################################
        #Calculo de la Variable de Proceso despues de salir del proceso 
        #Planta G(s)=K/(tau*S+1)=3.543/(0.56*s+1)

        self.Yn=(self.K*self.periodo*(self.u_act+self.u_ant2) + self.Yn_1*(2*self.tau-self.periodo))/ (2*self.tau+self.periodo)
        
        self.Yn_1=self.Yn #definiendo el valor de Yn_1

        #self.Yn=self.Yn*27.03-27.03 # escalando la señal del transmisor

        
        #########################################################################################
        #calculo del error actual
        e_act=SP-self.Yn
        
        
       
        ##########################################################################################
        #Controlador PI
        #Calculo de la Variable de Control CV, señal de exitacion de actuador
        
        Prop=(e_act- self.e_ant2)*Kp

        Int=(e_act + 2*self.e_ant + self.e_ant2)*(Ki*self.periodo)/2

        Der=(e_act - 2*self.e_ant + self.e_ant2)*(2*Kd/self.periodo)

        self.u_act= self.u_ant2 + Prop + Int + Der
        
        self.e_ant2 =self.e_ant
        self.e_ant  =e_act

        self.u_ant2 =self.u_ant
        self.u_ant  =self.u_act

        #self.u_act=self.u_act*0.1 # escalando la señal del actuador, convirtiendola en voltios.

        ##########################################################################################
        self.cola.put([self.Yn,self.u_act])

        print(self.i,tn,self.Yn,self.u_act)

        # Guardar fila 
        #writer.writerow([self.i,tn,self.Yn,self.u_act]) #¿para que?
        
        
class Frame(wx.Frame):

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
                self.szctrls = wx.FlexGridSizer(rows=6, cols=7, vgap=10, hgap=10)
                
                #se define las funciones canvas, controles y menu 
                self.initCanvas()
                self.initCtrls()
                self.initMenu()
                
                self.pcanvas.SetSizer(self.szcanvas) # una funcion dentro de otra funcion, esto es el decorado?
                self.pctrls.SetSizer(self.szctrls) #una funcion dentro de otra funcion, esto es decorado?
                
                self.szmain.Add(self.pcanvas, 1, wx.EXPAND)
                self.szmain.Add(self.pctrls, 1, wx.EXPAND)
                
                self.SetSizer(self.szmain)
                
                self.intervalo = [0.0,10.0]
                self.xlabel = "Tiempo(S)"
                self.ylabel = "% Caudal Deseado (SP)\n\n% Caudal Sensado (PV)\n\n Variable de Control (V)"
                self.Fit()
                #self.Centre(True)
                self.timer = wx.Timer(self)

                #Definir funcion asociada a timer
                self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        def OnTimer(self, event):
                self.tiempo = self.tiempo + Ts 

                [y,u]=self.cola.get() 
                
                #Dibujar punto
                self.axes.plot([self.tiempo,self.tiempo],[y,y], lw = 1, color='blue', marker='o', mfc = 'blue', mec = 'blue',  markersize = 5) # Gráfica
                self.axes.plot([self.tiempo],[u], lw = 1, color='green', marker='o', mfc = 'green', mec = 'green',  markersize = 5) # Gráfica
                self.axes.plot([self.tiempo],[SP], lw = 1, color='red', marker='o', mfc = 'red', mec = 'red',  markersize = 5) # Gráfica
                
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

                self.labelSP = wx.StaticText(self.pctrls, -1, "% Caudal Deseado (SP):", size=(210, 25))                
                self.txtSP= wx.TextCtrl(self.pctrls, -1)

                self.labelPV = wx.StaticText(self.pctrls, -1, "% Caudal Sensado (PV):", size=(210, 25))
                self.txtPV = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelCV = wx.StaticText(self.pctrls, -1, "% Variable de Control (CV):", size=(210, 25))
                self.txtCV = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelKP = wx.StaticText(self.pctrls, -1, " Kp : ", size=(40, 25))                
                self.txtKP = wx.TextCtrl(self.pctrls, -1)

                self.labelKI = wx.StaticText(self.pctrls, -1, " Ki : ", size=(40, 25))
                self.txtKI = wx.TextCtrl(self.pctrls, -1)
                
                self.labelKD = wx.StaticText(self.pctrls, -1, " Kd : ", size=(40, 25))
                self.txtKD = wx.TextCtrl(self.pctrls, -1)

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
                
                # Fuente
                mod_font = self.labelSP.GetFont()
                mod_font.SetPointSize(12)
                mod_font.SetWeight(wx.BOLD)

                #Set Point
                self.labelSP.SetFont(mod_font)
                self.txtSP.SetFont(mod_font)
                self.txtSP.SetForegroundColour((100,100,255))

                #Caudal Sensado
                self.labelPV.SetFont(mod_font)
                self.txtPV.SetFont(mod_font)
                self.txtPV.SetBackgroundColour((255,255,0))
                
                #Voltaje enviado a la valvula.
                self.labelCV.SetFont(mod_font)
                self.txtCV.SetFont(mod_font)
                self.txtCV.SetBackgroundColour((255,255,0))

                #Constante Proporcional
                self.labelKP.SetFont(mod_font)
                self.txtKP.SetFont(mod_font)
                self.txtKP.SetForegroundColour((100,100,255))

                #Constante Proporcional
                self.labelKI.SetFont(mod_font)
                self.txtKI.SetFont(mod_font)
                self.txtKI.SetForegroundColour((100,100,255))

                #Constante Derivativa
                self.labelKD.SetFont(mod_font)
                self.txtKD.SetFont(mod_font)
                self.txtKD.SetForegroundColour((100,100,255))
                
                self.Bind(wx.EVT_BUTTON, self.iniciar, self.botStart)
                self.Bind(wx.EVT_BUTTON, self.finalizar, self.botStop)
                self.Bind(wx.EVT_BUTTON, self.regresar, self.botBack)


                #Set Point
                self.szctrls.Add(self.labelSP, 1, wx.EXPAND)
                self.szctrls.Add(self.txtSP, 1, wx.EXPAND)

                #Constante Proporcional
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelKP, 1, wx.EXPAND)
                self.szctrls.Add(self.txtKP, 1, wx.EXPAND)
                
                #Caudal Sensado
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelPV, 1, wx.EXPAND)
                self.szctrls.Add(self.txtPV, 1, wx.EXPAND)

                #Constante Integral
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelKI, 1, wx.EXPAND)
                self.szctrls.Add(self.txtKI, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)

                #Voltaje enviado a la valvula
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelCV, 1, wx.EXPAND)
                self.szctrls.Add(self.txtCV, 1, wx.EXPAND)

                #Constante Derivativa
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelKD, 1, wx.EXPAND)
                self.szctrls.Add(self.txtKD, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)

                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botStart, 1, wx.ALL|wx.ALIGN_CENTER)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botStop, 1, wx.ALL|wx.ALIGN_CENTER)     
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botBack, 1, wx.ALL|wx.ALIGN_CENTER)     
                self.szctrls.AddSpacer(1)
               
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

                def es_real(valor):
   
                        try:
                                float(valor) # Intenta convertir a flotante
                                return True
                        except (ValueError, TypeError): # Captura errores si no es un número o no es compatible
                                return False
              
                # Verificar si es número entero
                if not es_real(valor):
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números con coma flotante", "Error", wx.OK | wx.ICON_ERROR)
                    return False

                numero = float(valor)

                # Validar rango
                if numero < 4 or numero > 70:
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("El valor debe estar entre 4 y 70", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                else:
                   txtCtrl.SetBackgroundColour(wx.NullColour)
                   txtCtrl.Refresh()
                   return True
        
        def isValid2(self,txtCtrl: wx.TextCtrl):

                valor = txtCtrl.GetValue()

                def es_real(valor):
   
                        try:
                                float(valor) # Intenta convertir a flotante
                                return True
                        except (ValueError, TypeError): # Captura errores si no es un número o no es compatible
                                return False
              
                # Verificar si es número entero
                if not es_real(valor):
                    
                    txtCtrl.SetBackgroundColour("red")
                    txtCtrl.Refresh()
                    wx.MessageBox("Solo se permiten números con coma flotante", "Error", wx.OK | wx.ICON_ERROR)
                    return False
                
                else:
                       txtCtrl.SetBackgroundColour(wx.NullColour)
                       txtCtrl.Refresh()
                       return True
             

        def iniciar(self,event):

                if not self.isValid1(self.txtSP):
                        
                    return
                if not self.isValid2(self.txtKP):
                    return
                if not self.isValid2(self.txtKI):
                    return
                if not self.isValid2(self.txtKD):
                    return
               
                global SP,Kp,Ki,Kd,op

                self.timer.Start(int(1000*Ts))    # ???....._____0.2 second interval self.timer.start()
                self.tiempo = 0
                self.axes.cla()
                self.intervalo = [0.0,10.0]
                self.axes.set_title('Tiempo vs %Caudal') # Configurar título de la gráfica
                self.axes.set_xlabel(self.xlabel)
                self.axes.set_ylabel(self.ylabel)

                self.SP = float(self.txtSP.GetValue())
                self.KP = float(self.txtKP.GetValue())
                self.KI = float(self.txtKI.GetValue())
                self.KD = float(self.txtKD.GetValue())

                SP=self.SP
                Kp=self.KP
                Ki=self.KI
                Kd=self.KD

                if op==0: # ????
                        op=1 # ????
                        t1=Timer1(0.1,Kp,self.cola) # ????
                        t1.actualizar() # ?????
                
        def finalizar(self,event):
                global det_muestreo
                self.timer.Stop()
                det_muestreo=1
                
        def guardar(self,event):

                wldc = "PNG (*.png)|*.png"
                dlg=wx.FileDialog(self, "Guardar", os.getcwd(), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=wldc)
                if dlg.ShowModal() == wx.ID_OK:
                        self.figure.savefig(dlg.GetPath())
                dlg.Destroy()

        def regresar(self,event):
                global f_data
                self.Close(True)
                f_data.close()
        
        def salir(self,event):
                global f_data
                self.Close(True)
                f_data.close()
                        
if __name__=='__main__':

        op=0
        print("sip")

        app = wx.App()
        frame = Frame(None,"Graficador",cola)
        frame.Show()
        app.MainLoop()

        