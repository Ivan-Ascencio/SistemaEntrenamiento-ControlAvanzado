# Sistema de Entrenamiento - Control Avanzado

Sistema de simulación para entrenamiento en control automático con diferentes procesos industriales.

## Descripción

Este proyecto contiene simuladores de diferentes procesos industriales con interfaces gráficas desarrolladas en wxPython para el aprendizaje y entrenamiento en técnicas de control avanzado.

## Procesos simulados

### 1. Intercambiador de Calor PUCP
- **DMC_Intercambiador.py** - Controlador DMC (Dynamic Matrix Control)
- **DMC_Intercambiador_Flops.py** - Versión con análisis de FLOPS para evaluación de carga computacional
- Modelos discretos, identificación de sistemas y control predictivo por matriz dinámica

### 2. Autoclave de Esterilización
- **GP_AutoclaveV2.py** - Control por Ganancia Programada (GP)
- Simulación de proceso térmico de esterilización

### 3. Control de Flujo
- **PID_Flujo.py** - Controlador PID convencional
- **PID_Flujo_DAQ.py** - Versión con adquisición de datos (DAQ)
- **Identificacion_Flujo.py** - Identificación de sistemas para el proceso de flujo
- **Identificacion_Flujo_DAQ.py** - Identificación con datos experimentales

### 4. Interfaz Principal
- **SistemaEntrenamiento.py** - Menú principal para acceder a todos los módulos

## Requisitos

- Python 3.10
- wxPython
- NumPy
- SciPy
- matplotlib
- control (python-control)
- random, subprocess (bibliotecas estándar)

## Uso

Ejecutar la interfaz principal:
`ash
python SistemaEntrenamiento.py
`

Desde la interfaz se puede acceder a cada módulo de simulación.

## Estructura del Repositorio

- Archivos *.py - Módulos de simulación y control
- Archivos *.png - Imágenes de las plantas para la interfaz gráfica
- Sustentacion.pptx - Material de sustentación
- __pycache__/ - Archivos compilados de Python

## Autor

Sistema desarrollado para entrenamiento en Control Avanzado - PUCP

## Licencia

Proyecto educativo
