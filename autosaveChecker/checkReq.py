#!/dls_sw/apps/python/anaconda/1.7.0/64/bin/python
import sys
import os
from epics import caget


# Run in the data dir and it will caget on all records in the .req files and print
# out which ones time out

localFiles = [f for f in os.listdir('.') if os.path.isfile(f)]
reqFiles = list()
for x in localFiles:
    if os.path.splitext(x)[1] == ".req":
        if len(x.split("-")) > 2:
            if x.split("-")[2] != "SIM":
                reqFiles.append(x)
        else:
            reqFiles.append(x)

print reqFiles

for index, arg in enumerate(reqFiles):
    print "Processing " + reqFiles[index]
    f = open(reqFiles[index], "r")
    recordString = ""
    inRecord = False
    for x in f:
        result = str(caget(x))
        if "cannot connect to" in result:
            print result

