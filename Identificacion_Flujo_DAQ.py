import nidaqmx
import matplotlib.pyplot as plt 
import csv
import time

plt.ion()
i=0 
j=0

u=-10 #señal de apertura de valvula , solo varia entre 25 y 40.
D=20 # aumentos sucesivos de 2 en 2
ug=0

#adquisicion de datos
t_i=nidaqmx.Task()
t_o=nidaqmx.Task()
t_i.ai_channels.add_ai_voltage_chan("Dev2/ai0")
t_o.ao_channels.add_ao_voltage_chan('Dev2/ao0')
t_o.timing.cfg_samp_clk_timing(1000) #por favor revisa esto , ¿es necesario? parace que es el tiempo muestreo

# CSV
f_data=open(r"ruta/data.csv","w",newline='')
writer=csv.writer(f_data)
writer.writerow(["n","t","u","y"])

ta=time.time()

while j<200:

    i=i+1
    tn=time.time()-ta # puede ser que no funcione

    print('1 Channel 1 Sample Write: ')
    
    if j<20:
        up=u
        t_o.write(up)
        ug=up*5+50

    elif j>=20:
        up=u+D
        t_o.write(up)
        ug=up*5+50
        
    plt.scatter(j, ug, color='green', label ='% de apertura de valvula') # tener cuidado con esta variacion
    
    
    y1=t_i.read(number_of_samples_per_channel=1)
    y=y1[0]*34.25-27.7
    
    plt.scatter(j, y, color='blue', label='% de variacion de Caudal')
    plt.xlabel('Tiempo(s)')
    plt.title ('Variacion del % Caudal con respecto al % de apertura de valvula ')
    plt.legend ()
    plt.pause(0.5) # analiza esta sentencia.

    writer.writerow([i,tn,ug,y])
    print (i,tn,ug,y)

    t_o.stop()
    j=j+1
   






