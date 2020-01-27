import os
import sys
import glob
from shutil import copyfile
import time


numOfFile = 1000
currentFile = 0
currentLength = 0
store = 0
timeStamps = list()
duration = list()

os.chdir("/ramdisk")


while (len(glob.glob('*')) < numOfFile):
    currentLength = len(glob.glob('*'))
    if (currentLength > currentFile):
        if (timeStamps.__len__()>0):
            timeStamps.append(int(round(time.time() * 1000)))
        else:
            timeStamps.append(int(round(time.time() * 1000)))

        currentFile = currentFile +1
        print currentFile



for a in timeStamps:
    if(duration.__len__()>0):
        duration.append((a-store))
        store = a
    else:
        store = a
        duration.append(a)


print timeStamps
print duration
plt.plot(duration)
plt.show()
