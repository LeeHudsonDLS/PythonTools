from cothread import *
from cothread.catools import *
import statistics

sleepTime = 2
#16mm
stepSize = 0.5

#X
#start = -9
#steps = 50

#Y
start = -12
steps = 52

baseMotorPV = 'FE24B-AL-SLITS-01:Y:PLUS'
motorCommand  =f'{baseMotorPV}.VAL'
encoder  =f'{baseMotorPV}.RBV'
dmovPV  =f'{baseMotorPV}.DMOV'
dmov = 1
potRaw = 'FE24B-CS-POT-01:ADC2_VALUE'
pot = f'{baseMotorPV}:POT'

encoderValues = list()
potValues = list()
potRawValues = list()


def dmovRead(value):
    global dmov
    dmov = value

camonitor(dmovPV, dmovRead)

Sleep(1)


for step in range(steps):
    caput(motorCommand,start+(step*stepSize))
    Sleep(0.5)
    while dmov == 0:
        Sleep(0.1)
        pass
    Sleep(0.5)
    encoderValues.append(caget(encoder))
    potValues.append(caget(pot))
    potRawValues.append(caget(potRaw))
    print(f'{encoderValues[-1]},{potValues[-1]},{potRawValues[-1]},{(encoderValues[-1]-potValues[-1])*1000}')
    #print(f'{encoderValues[-1]},{potRawValues[-1]}')

res = (encoderValues[-1] - encoderValues[0])/ (potRawValues[-1]-potRawValues[0])

print(f'Resolution = {res}')






quit()
