# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.2.1-111-g5faebfea)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import subprocess
import sys
import os

import gettext
_ = gettext.gettext

###########################################################################
## Class Sistema_Entrenamiento
###########################################################################

class Sistema_Entrenamiento ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Sistema de Entrenamiento"), pos = wx.DefaultPosition, size = wx.Size( 1112,720 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
        self.SetForegroundColour( wx.Colour( 0, 0, 0 ) )
        self.SetBackgroundColour( wx.Colour( 0, 0, 255 ) )

        gSizer1 = wx.GridSizer( 0, 2, 0, 0 )

        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer11 = wx.BoxSizer( wx.VERTICAL )

        self.m_button1 = wx.Button( self, wx.ID_ANY, _(u"Intercambiador \n        PUCP"), wx.DefaultPosition, wx.Size( 160,60 ), 0 )
        self.m_button1.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.m_button1.SetBackgroundColour( wx.Colour( 0, 255, 255 ) )

        bSizer11.Add( self.m_button1, 0, wx.ALL, 5 )

        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"El Intercambiador de \ncalor de la PUCP, sera \ncontrolado por un \nalgoritmo DMC\n(controlador de Matriz\nDinamica)."), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )

        self.m_staticText4.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.m_staticText4.SetBackgroundColour( wx.Colour( 255, 0, 213 ) )

        bSizer11.Add( self.m_staticText4, 0, wx.ALL, 5 )


        bSizer2.Add( bSizer11, 1, wx.EXPAND, 5 )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_bitmap1 = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( u"Intercambiador.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer3.Add( self.m_bitmap1, 0, wx.ALL, 5 )


        bSizer2.Add( bSizer3, 1, wx.EXPAND, 5 )


        gSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )

        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer12 = wx.BoxSizer( wx.VERTICAL )

        self.m_button2 = wx.Button( self, wx.ID_ANY, _(u"Autoclave de \nEsterilizacion"), wx.DefaultPosition, wx.Size( 160,60 ), 0 )
        self.m_button2.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.m_button2.SetBackgroundColour( wx.Colour( 0, 255, 255 ) )

        bSizer12.Add( self.m_button2, 0, wx.ALL, 5 )

        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"La Autoclave de \nEsterilizacion sera \ncontrolada por un\nalgoritmo GP \n(Ganancia \nProgramada)"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )

        self.m_staticText5.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.m_staticText5.SetBackgroundColour( wx.Colour( 255, 0, 213 ) )

        bSizer12.Add( self.m_staticText5, 0, wx.ALL, 5 )


        bSizer4.Add( bSizer12, 1, wx.EXPAND, 5 )

        bSizer5 = wx.BoxSizer( wx.VERTICAL )

        self.m_bitmap3 = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( u"AutoclaveEsterilizacion.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer5.Add( self.m_bitmap3, 0, wx.ALL, 5 )


        bSizer4.Add( bSizer5, 1, wx.EXPAND, 5 )


        gSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )

        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer13 = wx.BoxSizer( wx.VERTICAL )

        self.m_button3 = wx.Button( self, wx.ID_ANY, _(u"Identificacion \n       Flujo"), wx.DefaultPosition, wx.Size( 160,60 ), 0 )
        self.m_button3.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.m_button3.SetBackgroundColour( wx.Colour( 0, 255, 255 ) )

        bSizer13.Add( self.m_button3, 0, wx.ALL, 5 )

        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, _(u"La identificacion de \nla planta de flujo se \nrealizara a travez de\n un algoritmo no \nparametrico utilizando\nlas entradas y salidas \nAnalogicas de una \nDAQ NI-6008"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )

        self.m_staticText6.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.m_staticText6.SetBackgroundColour( wx.Colour( 255, 0, 213 ) )

        bSizer13.Add( self.m_staticText6, 0, wx.ALL, 5 )


        bSizer6.Add( bSizer13, 1, wx.EXPAND, 5 )

        bSizer8 = wx.BoxSizer( wx.VERTICAL )

        self.m_bitmap7 = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( u"ControlFlujo.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_bitmap7, 0, wx.ALL, 5 )


        bSizer6.Add( bSizer8, 1, wx.EXPAND, 5 )


        gSizer1.Add( bSizer6, 1, wx.EXPAND, 5 )

        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer14 = wx.BoxSizer( wx.VERTICAL )

        self.m_button4 = wx.Button( self, wx.ID_ANY, _(u"Control PID\n   Clasico"), wx.DefaultPosition, wx.Size( 160,60 ), 0 )
        self.m_button4.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.m_button4.SetBackgroundColour( wx.Colour( 0, 255, 255 ) )

        bSizer14.Add( self.m_button4, 0, wx.ALL, 5 )

        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, _(u"El control Clasico PID\nde la planta de Flujo\nde la PUCP\n, se realizara utilizando\nlas entradas y salidas \nAnalogicas de una \nDAQ NI-6008"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )

        self.m_staticText7.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
        self.m_staticText7.SetBackgroundColour( wx.Colour( 255, 0, 213 ) )

        bSizer14.Add( self.m_staticText7, 0, wx.ALL, 5 )


        bSizer7.Add( bSizer14, 1, wx.EXPAND, 5 )

        bSizer9 = wx.BoxSizer( wx.VERTICAL )

        self.m_bitmap8 = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( u"ControlFlujo.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer9.Add( self.m_bitmap8, 0, wx.ALL, 5 )


        bSizer7.Add( bSizer9, 1, wx.EXPAND, 5 )


        gSizer1.Add( bSizer7, 1, wx.EXPAND, 5 )


        self.SetSizer( gSizer1 )
        self.Layout()

        self.Centre( wx.BOTH )

        self.Bind(wx.EVT_BUTTON, self.iniciarIntercambiador, self.m_button1)
        self.Bind(wx.EVT_BUTTON, self.iniciarAutoclave, self.m_button2)
        self.Bind(wx.EVT_BUTTON, self.iniciarIdentificacion, self.m_button3)
        self.Bind(wx.EVT_BUTTON, self.iniciarControlPID, self.m_button4)

    def iniciarIntercambiador(self, event):

        subprocess.run([sys.executable, 'DMC_Intercambiador.py'])
        #os._exit(1)
        #sys.exit(1)
        #app=wx.App()
        #frame = DMC(None)
        #frame.Show()
        #app.MainLoop()




    def iniciarAutoclave(self,event):
        subprocess.run([sys.executable, 'GP_AutoclaveV2.py'])
        


    def iniciarIdentificacion(self,event):
        subprocess.run([sys.executable, 'Identificacion_Flujo.py'])


    def iniciarControlPID(self,event):
        subprocess.run([sys.executable, 'PID_Flujo.py'])




        

    def __del__( self ):
       pass


if __name__=='__main__':

    app = wx.App()
    frame = Sistema_Entrenamiento(None)
    frame.Show()
    app.MainLoop()