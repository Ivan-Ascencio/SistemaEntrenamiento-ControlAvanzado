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
import sys
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from numpy import sin, cos, tan, log, sqrt, exp, linspace

import subprocess
import SistemaEntrenamiento

cola = queue.LifoQueue()
matplotlib.use('WXAgg')

# ============================================================
#  CONTADOR GLOBAL DE FLOPs
# ============================================================
flops_total = 0          # acumulador global
flops_init  = 0          # FLOPs solo del __init__
flops_per_tick = []      # FLOPs por cada llamada a actualizar()

def reset_flops():
    global flops_total, flops_init, flops_per_tick
    flops_total    = 0
    flops_init     = 0
    flops_per_tick = []

# ---- Helpers para estimar FLOPs de operaciones numpy --------
def flops_matmul(A_shape, B_shape):
    """FLOPs de A @ B: 2*m*k*n  (mul + add por elemento)"""
    m, k = A_shape
    k2, n = B_shape
    assert k == k2, "dimensiones incompatibles"
    return 2 * m * k * n

def flops_inv(n):
    """FLOPs aproximados de inv(n×n): O(n^3) con factor ~2/3"""
    return int((2 / 3) * n ** 3)

def flops_matvec(rows, cols):
    """FLOPs de A @ v (vector): 2*rows*cols"""
    return 2 * rows * cols

# ============================================================

# ----- Planta discreta ----------------------------------
#
#                  0.0143 z^-11
#      ------------------------------------
#       1 - 1.827 z^-1 + 0.8343 z^-2

numd = [0.0143]
dend = [1, -1.827, 0.8343, 0, 0, 0, 0, 0, 0, 0, 0, 0]

Ts = 0.5
sistemad = tf(numd, dend, Ts)
[B, A] = tfdata(sistemad)
plantadis = tf(sistemad)

v = np.arange(0, 30, 0.5)
t1, y = step_response(sistemad, v)
datadgi = y

M_maximo = len(datadgi) - 1
gi = datadgi[0:len(datadgi)]


# ============================================================
class Timer1:

    def __init__(self, Tm, P, queue1):

        global det_muestreo, flops_total, flops_init

        det_muestreo = 0
        tick_flops   = 0          # FLOPs locales de __init__

        self.periodo = 0.5
        self.i       = 0
        self.cola    = queue1
        self.u_act   = 0
        self.ta      = time.time()

        self.u      = 0
        self.u_ant1 = self.u_ant2 = self.u_ant3  = 0
        self.u_ant4 = self.u_ant5 = self.u_ant6  = 0
        self.u_ant7 = self.u_ant8 = self.u_ant9  = 0
        self.u_ant10= self.u_ant11= 0

        self.ym      = 25
        self.ym_ant1 = 25
        self.ym_ant2 = 25

        self.yxm      = 25
        self.yxm_ant1 = 25
        self.yxm_ant2 = 25

        self.e_ant11 = self.e_ant10 = self.e_ant9  = 0
        self.e_ant8  = self.e_ant7  = self.e_ant6  = 0
        self.e_ant5  = self.e_ant4  = self.e_ant3  = 0
        self.e_ant2  = self.e_ant1  = self.e_act   = 0

        # ---- Construcción de G  --------------------------------
        self.G = []

        for self.a in range(0, N):
            self.C     = np.zeros((self.a, 1))
            self.D     = np.matrix(gi[1:Pred - self.a + 1]).T   # g1..g(P-a)
            self.arreglo = np.concatenate((self.C, self.D))
            self.G.append(self.arreglo)
            # FLOPs: concatenar = solo copias, ~0 aritmético

        self.G = np.squeeze(np.asarray(self.G))            # N × Pred
        self.G = self.G.transpose()                        # Pred × N, fila i = paso i+1

        # ---- Cálculo de Kc  ------------------------------------
        # Kc = inv(G'.delta.G + lambda*I) . G' . delta
        # Paso 1: G' @ delta  →  (N×Pred)(Pred×Pred) = N×Pred
        GtD_flops = flops_matmul((N, Pred), (Pred, Pred))
        tick_flops += GtD_flops

        # Paso 2: (G'delta) @ G  →  (N×Pred)(Pred×N) = N×N
        GtDG_flops = flops_matmul((N, Pred), (Pred, N))
        tick_flops += GtDG_flops

        # Paso 3: + lambda*I  →  N adiciones + N multiplicaciones
        tick_flops += 2 * N

        # Paso 4: inv(N×N)
        inv_flops = flops_inv(N)
        tick_flops += inv_flops

        # Paso 5: inv @ G'  →  (N×N)(N×Pred)
        invGt_flops = flops_matmul((N, N), (N, Pred))
        tick_flops += invGt_flops

        # Paso 6: result @ delta  →  (N×Pred)(Pred×Pred)
        KcD_flops = flops_matmul((N, Pred), (Pred, Pred))
        tick_flops += KcD_flops

        self.Matriz_K = np.dot(
            np.dot(
                np.linalg.inv(
                    np.dot(np.dot(self.G.T, delta), self.G) +
                    np.dot(lamda, np.eye(N))
                ),
                self.G.T
            ),
            delta
        )
        self.Kc = self.Matriz_K[0][:]

        self.duf = np.zeros((M, 1))

        self.B = np.squeeze(np.asarray(B))
        self.A = np.squeeze(np.asarray(A))

        self.ym = np.matrix([25])
        self.ym = np.concatenate((self.ym, np.full((15, 1), 25)))

        # Acumular FLOPs de __init__
        flops_init  += tick_flops
        flops_total += tick_flops

        print(f"\n{'='*55}")
        print(f"  FLOPs en __init__  (N={N}, Pred={Pred}, M={M})")
        print(f"  G\'.delta (matmul) : {GtD_flops:>10,}")
        print(f"  (G\'δ).G (matmul)  : {GtDG_flops:>10,}")
        print(f"  + λI              : {2*N:>10,}")
        print(f"  inv(N×N)          : {inv_flops:>10,}")
        print(f"  inv @ G\'          : {invGt_flops:>10,}")
        print(f"  result @ δ        : {KcD_flops:>10,}")
        print(f"  TOTAL __init__    : {tick_flops:>10,}")
        print(f"{'='*55}\n")

    # ----------------------------------------------------------
    def actualizar(self):

        global ta, writer, SP, CV, PV, delta, lamda, P, tau, Ruido
        global flops_total, flops_per_tick

        self.i += 1
        tn = time.time() - self.ta
        tick_flops = 0              # FLOPs de este tick

        # ---- Cambios de SP en el tiempo ----------------------
        if tn > 250:  SP = 35
        if tn > 500:  SP = 45
        if tn > 750:  SP = 35
        if tn > 1000: SP = 45

        self.ref = np.full((Pred, 1), SP)

        if det_muestreo == 0:
            self.timer = threading.Timer(self.periodo, self.actualizar)
            self.timer.start()

        # ---- Modelo de la planta  ----------------------------
        # yxm = B*u_ant11 - A[1]*ym_ant1 - A[2]*ym_ant2 + ruido
        #  → 2 mul + 2 mul + 2 sumas + 1 add_ruido  = 7 FLOPs
        tick_flops += 7

        # ym = B*u_ant11 - A[1]*ym_ant1 - A[2]*ym_ant2
        #  → 3 mul + 2 sumas = 5 FLOPs
        tick_flops += 5

        self.f = np.matrix([]).T

        self.yxm = self.B * self.u_ant11 - self.A[1] * self.ym_ant1 \
                   - self.A[2] * self.ym_ant2 + Ruido * random.randint(-2, 2)
        self.ym  = self.B * self.u_ant11 - self.A[1] * self.ym_ant1 \
                   - self.A[2] * self.ym_ant2

        # ---- Bucle de predicción  ----------------------------
        # Por cada kk (fila kk = paso de predicción kk+1):
        #   - vect_g: M restas gi[kk+2+j]-gi[1+j]      → M FLOPs
        #   - H = vect_g @ duf: producto punto (M)      → 2M FLOPs
        #   - ym + H: 1 suma                            → 1 FLOP
        # Total por iteración: 3M + 1
        loop_flops = Pred * (3 * M + 1)
        tick_flops += loop_flops

        for kk in range(0, Pred):
            self.vect_g = np.matrix(gi[kk + 2:kk + 2 + M] - gi[1:M + 1])
            self.H = np.dot(self.vect_g, self.duf)
            self.f = np.concatenate((self.f, self.ym + self.H))

        # ---- Ley de control  ---------------------------------
        # Vu_act = Kc @ (ref - f)
        # ref - f: Pred restas                          → Pred FLOPs
        # Kc @ (...): (1×Pred)(Pred×1)                 → 2*Pred FLOPs
        ctrl_flops = 3 * Pred
        tick_flops += ctrl_flops

        self.Vu_act = self.Kc * (self.ref - self.f)
        self.u = self.u + self.Vu_act

        # duf shift: solo asignaciones, ~0 aritmético
        self.desplaza = self.duf[1:M]
        self.duf = np.concatenate((self.Vu_act, self.desplaza))

        # ---- Saturación de salida  ---------------------------
        if self.yxm < 25:
            self.yf = 25
        if self.yxm >= 25:
            self.yf = self.yxm

        # ---- Actualización de estados (registros de retardo) -
        # Son asignaciones puras, FLOPs aritméticos = 1 (e_act = SP - ym)
        tick_flops += 1   # e_act = SP - ym

        self.e_ant11 = self.e_ant10
        self.e_ant10 = self.e_ant9
        self.e_ant9  = self.e_ant8
        self.e_ant8  = self.e_ant7
        self.e_ant7  = self.e_ant6
        self.e_ant6  = self.e_ant5
        self.e_ant5  = self.e_ant4
        self.e_ant4  = self.e_ant3
        self.e_ant3  = self.e_ant2
        self.e_ant2  = self.e_ant1
        self.e_ant1  = self.e_act
        self.e_act   = SP - self.ym

        self.u_ant11 = self.u_ant10
        self.u_ant10 = self.u_ant9
        self.u_ant9  = self.u_ant8
        self.u_ant8  = self.u_ant7
        self.u_ant7  = self.u_ant6
        self.u_ant6  = self.u_ant5
        self.u_ant5  = self.u_ant4
        self.u_ant4  = self.u_ant3
        self.u_ant3  = self.u_ant2
        self.u_ant2  = self.u_ant1
        self.u_ant1  = self.u

        self.ym_ant2 = self.ym_ant1
        self.ym_ant1 = self.ym

        # Acumular
        flops_per_tick.append(tick_flops)
        flops_total += tick_flops

        self.cola.put([float(self.yf), float(self.u)])
        print(f"[tick {self.i:4d}] t={tn:7.2f}s | "
              f"yf={float(self.yf):6.2f} | u={float(self.u):8.4f} | "
              f"FLOPs/tick={tick_flops:5,} | FLOPs acum.={flops_total:10,}")


# ============================================================
class FrameDMC(wx.Frame):

    def __init__(self, parent, title, cola1):

        wx.Frame.__init__(self, parent, title=title, pos=(1, 1))
        self.pcanvas = wx.Panel(self, -1)
        self.pctrls  = wx.Panel(self, -1)

        self.cola    = cola1
        self.tiempo  = 0
        self.ultimaT = 0
        self.TemperaturaD = 0

        self.szmain   = wx.FlexGridSizer(rows=2, cols=1, vgap=0, hgap=0)
        self.szcanvas = wx.BoxSizer(wx.VERTICAL)
        self.szctrls  = wx.FlexGridSizer(rows=6, cols=8, vgap=10, hgap=10)

        self.initCanvas()
        self.initCtrls()
        self.initMenu()

        self.pcanvas.SetSizer(self.szcanvas)
        self.pctrls.SetSizer(self.szctrls)

        self.szmain.Add(self.pcanvas, 1, wx.EXPAND)
        self.szmain.Add(self.pctrls,  1, wx.EXPAND)
        self.SetSizer(self.szmain)

        self.intervalo = [0.0, 10.0]
        self.xlabel    = "Tiempo(S)"
        self.ylabel    = "% Temperatura (°C)"
        self.Fit()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

    # ----------------------------------------------------------
    def OnTimer(self, event):
        self.tiempo += Ts
        y, u = self.cola.get()

        self.axes.plot([self.tiempo], [y],  lw=1, color='blue',  marker='o',
                       mfc='blue',  mec='blue',  markersize=2,
                       label='Temperatura Sensada (PV)')
        self.axes.plot([self.tiempo], [u],  lw=1, color='green', marker='o',
                       mfc='green', mec='green', markersize=2,
                       label='Variable de Control (CV)')
        self.axes.plot([self.tiempo], [SP], lw=1, color='red',   marker='o',
                       mfc='red',   mec='red',   markersize=2,
                       label='Temperatura Deseada (SP)')

        if self.tiempo <= 0.5:
            self.axes.legend(loc='upper left', fontsize='12')

        self.axes.grid(True)
        self.canvas.draw()

        self.txtPV.SetValue(str(y))
        self.txtCV.SetValue(str(u))

        # Mostrar FLOPs acumulados en la barra de título
        self.SetTitle(f"Graficador  |  FLOPs acum.: {flops_total:,}")

    # ----------------------------------------------------------
    def initCanvas(self):
        self.figure = Figure(figsize=(16, 5), dpi=100)
        self.axes   = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.pcanvas, -1, self.figure)
        self.szcanvas.Add(self.canvas, 1, wx.EXPAND)

    # ----------------------------------------------------------
    def initCtrls(self):

        def lbl(txt, w=210): return wx.StaticText(self.pctrls, -1, txt, size=(w, 25))
        def txt(ro=False):
            style = wx.TE_READONLY if ro else 0
            return wx.TextCtrl(self.pctrls, -1, '', style=style)

        self.labelSP    = lbl("% Temp. Deseada (SP):")
        self.txtSP      = txt()
        self.labelPV    = lbl("% Temp. Sensada (PV):")
        self.txtPV      = txt(ro=True)
        self.labelCV    = lbl("% Variable de Control (CV):", w=220)
        self.txtCV      = txt(ro=True)
        self.labelDelta = lbl("Delta :")
        self.txtDelta   = txt()
        self.labelLamda = lbl("Lamda :")
        self.txtLamda   = txt()
        self.labelPred  = lbl("Horizonte de Prediccion (P):", w=220)
        self.txtPred    = txt()
        self.labelHC    = lbl("Horizonte de control (N):", w=220)
        self.txtHC      = txt()
        self.labelHM    = lbl("Horizonte de Modelo (M):", w=220)
        self.txtHM      = txt()
        self.labelRuido = lbl("Ruido:", w=220)
        self.txtRuido   = txt()

        # ----- Botón FLOPs (nuevo) ----------------------------
        self.botFlops = wx.Button(self.pctrls, -1, "Ver FLOPs", size=(100, 25))
        self.botFlops.SetFont(wx.Font(11, wx.FONTFAMILY_ROMAN,
                                      wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,
                                      False, "Serif"))
        self.botFlops.SetBackgroundColour(wx.Colour(200, 100, 0))
        self.botFlops.SetForegroundColour(wx.WHITE)

        btn_style = dict(size=(80, 25),
                         font=wx.Font(11, wx.FONTFAMILY_ROMAN,
                                      wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD,
                                      False, "Serif"),
                         bg=wx.Colour(0, 126, 128),
                         fg=wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))

        def make_btn(label):
            b = wx.Button(self.pctrls, -1, label, size=btn_style['size'])
            b.SetFont(btn_style['font'])
            b.SetBackgroundColour(btn_style['bg'])
            b.SetForegroundColour(btn_style['fg'])
            return b

        self.botStart = make_btn("Start")
        self.botStop  = make_btn("Stop")
        self.botBack  = make_btn("Back")

        # Fuente común
        mod_font = self.labelSP.GetFont()
        mod_font.SetPointSize(12)
        mod_font.SetWeight(wx.BOLD)

        for w in [self.labelSP, self.txtSP, self.labelPV, self.txtPV,
                  self.labelCV, self.txtCV, self.labelDelta, self.txtDelta,
                  self.labelLamda, self.txtLamda, self.labelPred, self.txtPred,
                  self.labelHC, self.txtHC, self.labelHM, self.txtHM,
                  self.labelRuido, self.txtRuido]:
            w.SetFont(mod_font)

        self.txtSP.SetForegroundColour((100, 100, 255))
        self.txtPV.SetBackgroundColour((255, 255, 0))
        self.txtCV.SetBackgroundColour((255, 255, 0))
        self.txtDelta.SetForegroundColour((100, 100, 255))
        self.txtLamda.SetForegroundColour((100, 100, 255))
        self.txtPred.SetForegroundColour((100, 100, 255))
        self.txtHC.SetForegroundColour((100, 100, 255))
        self.txtHM.SetForegroundColour((100, 100, 255))
        self.txtRuido.SetForegroundColour((100, 100, 255))

        self.Bind(wx.EVT_BUTTON, self.iniciar,       self.botStart)
        self.Bind(wx.EVT_BUTTON, self.finalizar,     self.botStop)
        self.Bind(wx.EVT_BUTTON, self.regresar,      self.botBack)
        self.Bind(wx.EVT_BUTTON, self.mostrar_flops, self.botFlops)

        # Layout
        add = self.szctrls.Add
        sp  = self.szctrls.AddSpacer

        add(self.labelSP,    1, wx.EXPAND); add(self.txtSP,    1, wx.EXPAND)
        add(self.labelDelta, 1, wx.EXPAND); add(self.txtDelta, 1, wx.EXPAND)
        add(self.labelHC,    1, wx.EXPAND); add(self.txtHC,    1, wx.EXPAND)
        sp(1); sp(1)
        add(self.labelPV,    1, wx.EXPAND); add(self.txtPV,    1, wx.EXPAND)
        add(self.labelLamda, 1, wx.EXPAND); add(self.txtLamda, 1, wx.EXPAND)
        add(self.labelHM,    1, wx.EXPAND); add(self.txtHM,    1, wx.EXPAND)
        sp(1)
        sp(1)
        add(self.labelCV,    1, wx.EXPAND); add(self.txtCV,    1, wx.EXPAND)
        add(self.labelPred,  1, wx.EXPAND); add(self.txtPred,  1, wx.EXPAND)
        add(self.labelRuido, 1, wx.EXPAND); add(self.txtRuido, 1, wx.EXPAND)
        sp(1); sp(1)
        add(self.botStart,  1, wx.ALL | wx.ALIGN_CENTER); sp(1); sp(1)
        add(self.botStop,   1, wx.ALL | wx.ALIGN_CENTER); sp(1); sp(1)
        add(self.botBack,   1, wx.ALL | wx.ALIGN_CENTER); sp(1)
        add(self.botFlops,  1, wx.ALL | wx.ALIGN_CENTER)

    # ----------------------------------------------------------
    def initMenu(self):
        m_archivo = wx.Menu()
        guardar   = m_archivo.Append(-1, "Guardar")
        salir     = m_archivo.Append(-1, "Salir")
        menu_bar  = wx.MenuBar()
        menu_bar.Append(m_archivo, "Archivo")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.guardar, guardar)
        self.Bind(wx.EVT_MENU, self.salir,   salir)

    # ----------------------------------------------------------
    # Validadores
    def _validate_int_range(self, ctrl, lo, hi, msg=None):
        val = ctrl.GetValue()
        if not val.isdigit():
            ctrl.SetBackgroundColour("red"); ctrl.Refresh()
            wx.MessageBox("Solo se permiten números enteros positivos", "Error",
                          wx.OK | wx.ICON_ERROR)
            return False
        n = int(val)
        if not (lo <= n <= hi):
            ctrl.SetBackgroundColour("red"); ctrl.Refresh()
            wx.MessageBox(msg or f"El valor debe estar entre {lo} y {hi}", "Error",
                          wx.OK | wx.ICON_ERROR)
            return False
        ctrl.SetBackgroundColour(wx.NullColour); ctrl.Refresh()
        return True

    def isValid1(self, c): return self._validate_int_range(c, 35, 45)
    def isValid2(self, c): return self._validate_int_range(c,  1,  1, "El valor debe ser 1")
    def isValid3(self, c): return self._validate_int_range(c,  1, 28)
    def isValid4(self, c): return self._validate_int_range(c,  5, 24)
    def isValid5(self, c): return self._validate_int_range(c,  5, 24)
    def isValid6(self, c): return self._validate_int_range(c,  5, 24)

    # ----------------------------------------------------------
    def iniciar(self, event):
        if not all([self.isValid1(self.txtSP),
                    self.isValid2(self.txtDelta),
                    self.isValid3(self.txtLamda),
                    self.isValid4(self.txtPred),
                    self.isValid5(self.txtHC),
                    self.isValid6(self.txtHM)]):
            return

        global SP, lamda, delta, Pred, op, M, N, Ruido

        self.timer.Start(int(1000 * Ts))
        self.tiempo = 0
        self.axes.cla()
        self.axes.set_title('Tiempo vs %Temperatura')
        self.axes.set_xlabel(self.xlabel)
        self.axes.set_ylabel(self.ylabel)

        SP    = float(self.txtSP.GetValue())
        delta = float(self.txtDelta.GetValue())
        lamda = float(self.txtLamda.GetValue())
        Pred  = int(self.txtPred.GetValue())
        N     = int(self.txtHC.GetValue())
        M     = int(self.txtHM.GetValue())
        Ruido = float(self.txtRuido.GetValue())

        reset_flops()           # ← reiniciar contadores al iniciar

        if op == 0:
            op = 1
            t1 = Timer1(0.1, delta, self.cola)
            t1.actualizar()

    # ----------------------------------------------------------
    def finalizar(self, event):
        global det_muestreo
        self.timer.Stop()
        det_muestreo = 1

    # ----------------------------------------------------------
    def mostrar_flops(self, event):
        """Muestra un resumen de FLOPs en un cuadro de diálogo."""
        ticks = len(flops_per_tick)
        prom  = int(sum(flops_per_tick) / ticks) if ticks else 0
        msg = (
            f"{'─'*45}\n"
            f"  RESUMEN DE FLOPs\n"
            f"{'─'*45}\n"
            f"  FLOPs en __init__    : {flops_init:>12,}\n"
            f"  FLOPs en actualizar  : {flops_total - flops_init:>12,}\n"
            f"  Ticks ejecutados     : {ticks:>12,}\n"
            f"  FLOPs promedio/tick  : {prom:>12,}\n"
            f"{'─'*45}\n"
            f"  TOTAL FLOPs          : {flops_total:>12,}\n"
            f"{'─'*45}"
        )
        wx.MessageBox(msg, "Contador de FLOPs", wx.OK | wx.ICON_INFORMATION)

    # ----------------------------------------------------------
    def guardar(self, event):
        wldc = "PNG (*.png)|*.png"
        dlg  = wx.FileDialog(self, "Guardar", os.getcwd(),
                             style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                             wildcard=wldc)
        if dlg.ShowModal() == wx.ID_OK:
            self.figure.savefig(dlg.GetPath())
        dlg.Destroy()

    def regresar(self, event):
        global det_muestreo
        self.timer.Stop()
        det_muestreo = 1
        subprocess.Popen(['python3', 'SistemaEntrenamiento.py'])
        sys.exit(FrameDMC)

    def salir(self, event):
        self.Close(True)


# ============================================================
if __name__ == '__main__':
    op = 0
    app   = wx.App()
    frame = FrameDMC(None, "Graficador", cola)
    frame.Show()
    app.MainLoop()