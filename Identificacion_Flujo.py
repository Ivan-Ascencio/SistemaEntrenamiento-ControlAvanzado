import wx
import os
import matplotlib
import random
import csv
import time
import threading
import queue
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
#writer=csv.writer(f_data)
#writer.writerow(["n","t","y","u"])
        
class Timer1:
        
    def __init__(self,Tm,P,queue1): # que es queue1
        
        global det_muestreo
        det_muestreo=0

        self.periodo=TS
        self.i=0
        self.Kp=10
        self.Ki=1
        self.cola=queue1
        self.y1=0
        self.a=0.95
        self.b=0.1
        self.u=5
        self.I=0
        self.D=10
        self.ta=time.time()

    def actualizar(self):

        global ta,writer,AI,AF,TE,TS
       
        self.i=self.i+1 
        tn=time.time()-self.ta 

        if det_muestreo==0:
                self.timer = threading.Timer(self.periodo,self.actualizar) 
                self.timer.start()

        
        if tn<TE:
                self.up=AI

        elif tn>TE:
                self.up=AF
        
        y1=2*self.up

        print(self.i,tn,y1,self.up)

        self.cola.put([y1,self.up]) # 

        # Guardar fila 
        writer.writerow([self.i,tn,y1,self.u]) #¿para que?
        
        

class Frame(wx.Frame):

        def __init__(self,parent,title,cola1):

                wx.Frame.__init__(self,parent,title=title, pos=(1,1))

                self.pcanvas = wx.Panel(self,-1)# que hace la funcion wx.panel?
                self.pctrls = wx.Panel(self,-1)

                self.cola=cola1
                self.tiempo = 0
                self.ultimaT = 0
                self.TemperaturaD = 0

                # Principal cuadro
                self.szmain = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0) #que hace la funcion wxFlexGridSizer

                # Cuadros internos al principal
                self.szcanvas = wx.BoxSizer(wx.VERTICAL) #que hace la funcion wx.BoxSizer y que hace la funcion wx.VERTICAL
                self.szctrls = wx.FlexGridSizer(rows=10, cols=6, vgap=10, hgap=10)
                
                #se define las funciones canvas, controles y menu 
                self.initCanvas()
                self.initCtrls()
                self.initMenu()
                
                self.pcanvas.SetSizer(self.szcanvas) # una funcion dentro de otra funcion, esto es el decorado?
                self.pctrls.SetSizer(self.szctrls) #una funcion dentro de otra funcion, esto es decorado?
                
                self.szmain.Add(self.pcanvas, 1, wx.EXPAND) # añade la grafica
                self.szmain.Add(self.pctrls, 1, wx.EXPAND) # añade lo controles
                
                self.SetSizer(self.szmain)# no entiendo?

                self.intervalo = [0.0,10.0]
                self.xlabel = "Tiempo(S)"
                self.ylabel = "Apertura(%)\nCaudal(%)"
                self.Fit()
                self.Centre(True)

                self.timer = wx.Timer(self) # esta llamando a otro timer ..........un timer distinto al Timer1
                self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer) #Definir funcion asociada a timer

        def OnTimer(self, event):

                self.tiempo = self.tiempo + TS 
                [y,u]=self.cola.get() #extrae los datos de la clase Timer1
                
                #Dibujar punto
                self.axes.plot([self.tiempo],[y], lw = 1, color='blue', marker='o', mfc = 'blue', mec = 'blue', linestyle = 'solid', markersize = 5, label='% Caudal') # Gráfica
                self.axes.plot([self.tiempo],[u], lw = 1, color='green', marker='o', mfc = 'green', mec = 'green',  markersize = 5) # Gráfica
                

                self.axes.grid(True) #Coloca rejilla
                self.canvas.draw() #Redibuja el elementos "canvas"
                
                self.txtVC.SetValue(str(y)) # ingresa el valor de y
                
        def initCanvas(self):
                # Creamos Figura
                self.figure = Figure(figsize=(15, 5), dpi=100) #esta pertenece a la clase figura
                self.axes = self.figure.add_subplot(111) # aqui se define self.axes
                
                # FigureCanvas
                self.canvas = FigureCanvas(self.pcanvas, -1, self.figure)
                self.szcanvas.Add(self.canvas, 1, wx.EXPAND)
                
                
        def initCtrls(self):
                #colores = "rojo verde azul negro amarillo".split()
                #estilos = "- -- -.".split()
                self.labelAI = wx.StaticText(self.pctrls, -1, " Valor Inicial Apertura (%)  : ", size=(200, 25))                
                self.txtAI = wx.TextCtrl(self.pctrls, -1)

                self.labelAF = wx.StaticText(self.pctrls, -1, " Valor Final Apertura (%)   : ", size=(200, 25))
                self.txtAF = wx.TextCtrl(self.pctrls, -1)

                self.labelVC = wx.StaticText(self.pctrls, -1, " Valor Caudal (%)             : ", size=(200, 25))
                self.txtVC = wx.TextCtrl(self.pctrls, -1, '', style=wx.TE_READONLY)

                self.labelTE = wx.StaticText(self.pctrls, -1, " Tiempo de escalon (s) : ", size=(200, 25))                
                self.txtTE = wx.TextCtrl(self.pctrls, -1)

                self.labelTS = wx.StaticText(self.pctrls, -1, " Periodo (Ts) : ", size=(40, 25))
                self.txtTS = wx.TextCtrl(self.pctrls, -1)


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
                mod_font = self.labelAI.GetFont()
                mod_font.SetPointSize(12)
                mod_font.SetWeight(wx.BOLD)

                #Valor Inicial del escalon
                self.labelAI.SetFont(mod_font)
                self.txtAI.SetFont(mod_font)
                self.txtAI.SetForegroundColour((100,100,255))

                #Valor Final del escalon
                self.labelAF.SetFont(mod_font)
                self.txtAF.SetFont(mod_font)
                self.txtAF.SetForegroundColour((100,100,255))

                #Error
                self.labelVC.SetFont(mod_font)
                self.txtVC.SetFont(mod_font)
                self.txtVC.SetBackgroundColour((100,100,255))

                #Proporcional
                self.labelTE.SetFont(mod_font)
                self.txtTE.SetFont(mod_font)
                self.txtTE.SetForegroundColour((100,100,255))

                #Integral
                self.labelTS.SetFont(mod_font)
                self.txtTS.SetFont(mod_font)
                self.txtTS.SetForegroundColour((100,100,255))
                
                self.Bind(wx.EVT_BUTTON, self.iniciar, self.botStart)
                self.Bind(wx.EVT_BUTTON, self.finalizar, self.botStop)
                self.Bind(wx.EVT_BUTTON, self.regresar, self.botBack)

                #Ubicacion
                
                #Valor inicial del escalon
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelAI, 1, wx.EXPAND)
                self.szctrls.Add(self.txtAI, 1, wx.EXPAND)

                #Constante proporcional
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelTE, 1, wx.EXPAND)
                self.szctrls.Add(self.txtTE, 1, wx.EXPAND)

                #Valor final del escalon
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelAF, 1, wx.EXPAND)
                self.szctrls.Add(self.txtAF, 1, wx.EXPAND)
                
                #Constante Integral
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelTS, 1, wx.EXPAND)
                self.szctrls.Add(self.txtTS, 1, wx.EXPAND)
                
                #Error
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.labelVC, 1, wx.EXPAND)
                self.szctrls.Add(self.txtVC, 1, wx.EXPAND)
                
                #Start
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botStart, 1, wx.ALL|wx.ALIGN_CENTER)

                #Stop
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botStop, 1, wx.ALL|wx.ALIGN_CENTER)

                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.Add(self.botBack, 1, wx.ALL|wx.ALIGN_CENTER)      
                
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                self.szctrls.AddSpacer(1)
                
        def initMenu(self):

                m_archivo = wx.Menu()
                guardar = m_archivo.Append(-1, "Guardar")
                salir = m_archivo.Append(-1, "Salir")
                menu_bar = wx.MenuBar()
                menu_bar.Append(m_archivo, "Archivo")
                self.SetMenuBar(menu_bar)
                
                self.Bind(wx.EVT_MENU, self.guardar, guardar)
                self.Bind(wx.EVT_MENU, self.salir, salir)
        

        def iniciar(self,event):

                global AI,AF,TE,TS,op 
                self.timer.Start(int(1000*TS)) # self.timer.Start(1000) es igual a 1 segungo de intervalo 
                self.tiempo = 0

                self.axes.cla()
                self.intervalo = [0.0,10.0]
                self.axes.set_title('Tiempo vs Caudal') #Configurar título de la gráfica
                self.axes.set_xlabel(self.xlabel)
                self.axes.set_ylabel(self.ylabel)
               

                self.AI= int(self.txtAI.GetValue())
                self.AF= int(self.txtAF.GetValue())
                self.TE= int(self.txtTE.GetValue())
                self.TS= float(self.txtTS.GetValue())

                AI=self.AI#aqui
                AF=self.AF
                TE=self.TE
                TS=self.TS

                if op==0: # ????
                        op=1 # ????
                        t1=Timer1(0.1,None,self.cola) # crea el objeto t1 que genera los datos
                        t1.actualizar() #muestra la funcion actualizar del objeto t1
                
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

        AF=0 
        AI=0
        TE=0
        Ki=1
        op=0
        TS=0
        print("sip")

        app = wx.App()
        frame = Frame(None,"Graficador",cola)
        frame.Show()
        app.MainLoop()

        