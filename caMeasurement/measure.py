from cothread import *
from cothread.catools import *
import statistics

sleepTime = 2
iterations = 20
outerLoop = 5
valPV = 'BL99I-MO-ROBOT-01:NEXT_PIN'
rbvPV = 'BL99I-MO-ROBOT-01:NEXT_PIN_RBV'
valPVVal = 10
firstpassRbv = True
firstpassVal = True
valTimestamps = list()
rbvTimestamps = list()

deltaTime = list()




def rbvValueRead(value):
    global firstpassRbv
    global rbvTimestamps
    if firstpassRbv:
        firstpassRbv = False 
    else:
        rbvTimestamps.append(value.timestamp)


def valValueRead(value):
    global firstpassVal
    global valTimestamps
    if firstpassVal:
        firstpassVal = False
    else:
        valTimestamps.append(value.timestamp)


 
camonitor(rbvPV, rbvValueRead,format = FORMAT_TIME)
camonitor(valPV, valValueRead,format = FORMAT_TIME)

Sleep(1)

for b in range(outerLoop):
    valPVVal = 10
    for a in range(iterations):
        caput(valPV,valPVVal)
        valPVVal+=1
        Sleep(sleepTime)


for v,r in zip(valTimestamps,rbvTimestamps):
    deltaTime.append(r-v)

print(f"Response times over {iterations} iterations:")
for a in deltaTime:
    print(a)


mean = statistics.mean(deltaTime)
sd = statistics.stdev(deltaTime)
med = statistics.median(deltaTime)
maximum = max(deltaTime)
minimum = min(deltaTime)

print(f"Mean = {mean}")
print(f"Standard deviation = {sd}")
print(f"Median = {med}")
print(f"Max = {maximum}")
print(f"Min = {minimum}")

quit()
