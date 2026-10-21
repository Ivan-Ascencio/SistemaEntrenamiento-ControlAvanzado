
# Librerías
import wx
import os
import matplotlib
import random
import csv
import time
import threading
import queue
import nidaqmx

matplotlib.use('WXAgg')

import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from numpy import sin,cos,tan,log,sqrt,exp,linspace

# Registro de data
f_data=open("data.csv","w",newline='')
writer=csv.writer(f_data)
writer.writerow(["n","t","y","u"])


# Cola para guardar data
cola=queue.LifoQueue()


#Tiempo de muestreo
Tm=0.1

# Tiempo de refresco
Ts=0.5 #segundos
ta=time.time()
Kp=5
Ki=1

class Timer1:
        def __init__(self,Tm,queue1): # que es queue1
        
                # Para detener muestreo
                global detener_muestreo
                detener_muestreo=0

                self.periodo=Tm
                self.i=0
                self.Kp=10 # Componente proporcional
                self.Ki=1 # Componente Integral
                self.cola=queue1
                self.y=0
                self.a=0.95
                self.b=0.1
                self.u=0
                self.I=0

                # Daq Task
                self.t_i=nidaqmx.Task()
                self.t_o=nidaqmx.Task()
                self.t_i.ai_channels.add_ai_voltage_chan("Dev1/ai0")
                self.t_o.ao_channels.add_ao_voltage_chan('Dev1/ao0')
                self.t_o.timing.cfg_samp_clk_timing(1000)


        try:
                
                with nidaqmx.Task() as task:
        # Configurar el canal analógico para la NI 6008 (ejemplo con "Dev1/ai0")
        # Asegúrate de reemplazar "Dev1" por el nombre de tu dispositivo
                        task.ai_channels.add_ai_voltage_chan("Dev1/ai0")

        # Configurar el timing si es necesario (ej: adquisición continua)
        # task.timing.cfg_samp_clk_timing(1000, source="", sample_mode=AcquisitionType.CONTINUOUS)

                        print("Iniciando lectura de datos...")
                
        except Exception as e: 

                app=wx.App()
                print("DAQ no detectada")
                wx.MessageBox(f"Un error crítico ocurrió , la DAQ no fue detectada: {e}", "Error", wx.OK | wx.ICON_ERROR)

         

        def actualizar(self):

        
                global ta,writer,objetivo
                
                #Contador
                self.i=self.i+1

                # Tiempo
                tn=time.time()-ta 

                # Timer periodico, aqui se define el periodo de muestreo.
                if detener_muestreo == 0:
                        self.timer=threading.Timer(self.periodo,self.actualizar) #.periodo
                        self.timer.start()

                # Lectura de señal analoga del transmisor
                self.y1 = self.t_i.read(number_of_samples_per_channel=1)
                self.y=self.y1[0]
                
                # escalando los valores de ingreso del transmisor /////  27.8*self.y1[0]-22.2
                def escalar(x):
                        return(27.8*x-22) 
                y=escalar(self.y) 

                # Estimacion del error (SP= Set Point , y= valor de caudal proveninte del transmisor)
                error=SP-y
                #Componente integral
                self.I=self.I + error*self.periodo
                #Señal de control (Kp= compnente proporcional , ki= componente integral)
                self.u=self.Kp*error + self.Ki*self.I

                #Saturacion
                if self.u > 10:
                        self.u=10
                if self.u < 0:
                        self.u=0
                
                #Envia la señal de control a la DAQ
                self.t_o.write(self.u)

                # Guardar fila en cola
                self.cola.put([y1,self.u]) 

                # Guarda valores en tabla
                writer.writerow([self.i,tn,y1,self.u])
        
        



        

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
                self.szcanvas = wx.BoxSizer(wx.VERTICAL)
                self.szctrls = wx.FlexGridSizer(rows=6, cols=7, vgap=10, hgap=10)
                
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
                self.ylabel = "Temperatura(°C)"
                self.Fit()
                #self.Centre(True)
                self.timer = wx.Timer(self)

                #Definir funcion asociada a timer
                self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        def OnTimer(self, event):
                self.tiempo = self.tiempo + Ts

                [y,u]=self.cola.get() ##como funciona la cola

                #Dibujar punto
                self.axes.plot([self.tiempo],[y], lw = 1, color='green', marker='o', mfc = 'blue', mec = 'blue',  markersize = 4) # Gráfica
                self.axes.plot([self.tiempo],[u], lw = 1, color='green', marker='o', mfc = 'green', mec = 'green',  markersize = 4) # Gráfica
                self.axes.plot([self.tiempo],[0], lw = 1, color='green', marker='o', mfc = 'black', mec = 'black',  markersize = 4) # Gráfica
                self.axes.plot([self.tiempo,self.tiempo+Ts],[self.TemperaturaD,self.TemperaturaD], lw = 1, color='red', marker='o', mfc = 'blue', mec = 'blue',  markersize = 2) # Gráfica
                self.axes.grid(True) # Coloca rejilla
                self.canvas.draw() # Redibuja el elementos "canvas"

                self.txtTR.SetValue(str(y))
                self.txtER.SetValue(str(y-self.TemperaturaD))
                
        def initCanvas(self):
                # Creamos Figure
                self.figure = Figure(figsize=(12, 5), dpi=100)
                self.axes = self.figure.add_subplot(111)
                
                # FigureCanvas
                self.canvas = FigureCanvas(self.pcanvas, -1, self.figure)
                
                self.szcanvas.Add(self.canvas, 1, wx.EXPAND)
                
                
        def initCtrls(self):
                #colores = "rojo verde azul negro amarillo".split()
                #estilos = "- -- -.".split()
                self.labelTD = wx.StaticText(self.pctrls, -1, " Temperatura Deseada : ", size=(200, 25))                
                self.txtTD = wx.TextCtrl(self.pctrls, -1)
                self.labelTR = wx.StaticText(self.pctrls, -1, " Temperatura Real    : ", size=(200, 25))
                self.txtTR = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)
                self.labelER = wx.StaticText(self.pctrls, -1, " Error               : ", size=(200, 25))
                self.txtER = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)
                self.labelKP = wx.StaticText(self.pctrls, -1, " Kp : ", size=(40, 25))                
                self.txtKP = wx.TextCtrl(self.pctrls, -1)
                self.labelKI = wx.StaticText(self.pctrls, -1, " Ki : ", size=(40, 25))
                self.txtKI = wx.TextCtrl(self.pctrls, -1)
                self.labelKD = wx.StaticText(self.pctrls, -1, " Kd : ", size=(40, 25))
                self.txtKD = wx.TextCtrl(self.pctrls, -1)
                self.botStart = wx.Button(self.pctrls, -1, "Start", size=(80, 25))
                self.botStop = wx.Button(self.pctrls, -1, "Stop", size=(80, 25))
                #self.color = wx.ComboBox(self.pctrls, -1, choices = colores, value='Color', size=(80,-1))
                #self.estilo = wx.ComboBox(self.pctrls, -1, choices = estilos, value='Estilo', size=(80,-1))
                
                # Fuente
                mod_font = self.labelTD.GetFont()
                mod_font.SetPointSize(12)
                mod_font.SetWeight(wx.BOLD)
                self.labelTD.SetFont(mod_font)
                self.txtTD.SetFont(mod_font)
                self.txtTD.SetForegroundColour((100,100,255))
                self.labelTR.SetFont(mod_font)
                self.txtTR.SetFont(mod_font)
                self.txtTR.SetBackgroundColour((255,255,0))
                self.labelER.SetFont(mod_font)
                self.txtER.SetFont(mod_font)
                self.txtER.SetBackgroundColour((255,255,0))
                self.labelKP.SetFont(mod_font)
                self.txtKP.SetFont(mod_font)
                self.txtKP.SetForegroundColour((100,100,255))
                self.labelKI.SetFont(mod_font)
                self.txtKI.SetFont(mod_font)
                self.txtKI.SetForegroundColour((100,100,255))
                self.labelKD.SetFont(mod_font)
                self.txtKD.SetFont(mod_font)
                self.txtKD.SetForegroundColour((100,100,255))
                
                self.Bind(wx.EVT_BUTTON, self.iniciar, self.botStart)
                self.Bind(wx.EVT_BUTTON, self.finalizar, self.botStop)
                
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelTD, 1, wx.EXPAND)
                self.szctrls.Add(self.txtTD, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelKP, 1, wx.EXPAND)
                self.szctrls.Add(self.txtKP, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)
                
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelTR, 1, wx.EXPAND)
                self.szctrls.Add(self.txtTR, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelKI, 1, wx.EXPAND)
                self.szctrls.Add(self.txtKI, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)

                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelER, 1, wx.EXPAND)
                self.szctrls.Add(self.txtER, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelKD, 1, wx.EXPAND)
                self.szctrls.Add(self.txtKD, 1, wx.EXPAND)
                self.szctrls.AddSpacer(1)

                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botStart, 1, wx.ALL|wx.ALIGN_CENTER)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botStop, 1, wx.ALL|wx.ALIGN_CENTER)     
                self.szctrls.AddSpacer(1)

                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)

                #self.szctrls.AddGrowableRow(6,1) # "Expandir" el TextCtrl 
                #self.szctrls.AddGrowableCol(7,1) # "Expandir" el TextCtrl 
                
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
        

        def iniciar(self,event):
                global SP,op, Tm

                self.timer.Start(int(1000*Ts))    # ¿0.2 second interval?
                self.tiempo = 0
                self.axes.cla()
                self.intervalo = [0.0,10.0]
                self.axes.set_title('Tiempo vs Temperatura') # Configurar título de la gráfica
                self.axes.set_xlabel(self.xlabel)
                self.axes.set_ylabel(self.ylabel)
                self.TemperaturaD = int(self.txtTD.GetValue())

                #Señal de referencia en grados Celsius
                SP=self.TemperaturaD

                #Señal de referencia en V
                #SP=

                if op==0: 
                        op=1 
                        t1=Timer1(Tm,self.cola)
                        t1.actualizar()
                
                '''try:
                        t1.actualizar()

                except Exception as e:
                        print("DAQ no detectada",e)
                        wx.MessageBox("Daq no detectada", "Error", wx.OK | wx.ICON_ERROR)'''
                        
                
        def finalizar(self,event):
                global detener_muestreo
                self.timer.Stop()
                detener_muestreo=1

                
                
        def guardar(self,event):
                wldc = "PNG (*.png)|*.png"
                dlg=wx.FileDialog(self, "Guardar", os.getcwd(), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard=wldc)
                if dlg.ShowModal() == wx.ID_OK:
                        self.figure.savefig(dlg.GetPath())
                dlg.Destroy()
        
        def salir(self,event):
                global f_data
                self.Close(True)
                f_data.close()
                
        
                
if __name__=='__main__':
        SP=0
        op=0
        print("sip")

        app = wx.App()
        frame = Frame(None,"Graficador",cola)
        frame.Show()
        app.MainLoop()

        