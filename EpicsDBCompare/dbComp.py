import sys
import os


  
inRecord = False
recordlist = list()
recordString = ""
noOfRecords = 0
metaDataString = ""
recordInstances = {
                    'aai':0,
                    'aao':0,
                    'ai':0,
                    'ao':0,
                    'aSub':0,
                    'bi':0,
                    'bo':0,
                    'calc':0,
                    'calcout':0,
                    'compress':0,
                    'dfanout':0,
                    'histogram':0,
                    'longin':0,
                    'longout':0,
                    'mbbi':0,
                    'mbbiDirect':0,
                    'permissive':0,
                    'sel':0,
                    'seq':0,
                    'state':0,
                    'stringin':0,
                    'stringout':0,
                    'subArray':0,
                    'sub':0,
                    'waveform':0,
}

localFiles = [f for f in os.listdir('.') if os.path.isfile(f)]
databaseFiles = list()
for x in localFiles:
    if os.path.splitext(x)[1] == ".db" or os.path.splitext(x)[1] == ".template" or os.path.splitext(x)[1] == ".vdb":
        databaseFiles.append(x)

print databaseFiles

for index, arg in enumerate(databaseFiles):
    print "Processing " + databaseFiles[index]
    f = open(databaseFiles[index], "r")
    recordString = ""
    inRecord = False
    for x in f:
        if inRecord == True:
            recordString += x
            if "}" in x:
                recordlist.append(recordString)
                recordString = ""
                inRecord = False 
        if "record(" in x and "#" not in x:
            for key in recordInstances.keys():
                if key + "," in x:
                    recordInstances[key]+=1
            recordString += x
            noOfRecords += 1
            inRecord = True

recordlist.sort()

for record in recordInstances:
    if recordInstances[record] > 0:
        metaDataString = metaDataString + record + ":" + str(recordInstances[record]) + "\n"

with open('result.txt','w') as f:
    f.write("%s" % metaDataString)
    for item in recordlist:
        f.write("%s" % item)

print "Total number of records: " + str(noOfRecords) + "\n"
print "Number of record instances:"
print metaDataString

print "Database written to result.txt\n"

