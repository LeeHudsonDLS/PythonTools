import sys
import os


  
pvList = list()
noOfPVs = 0


localFiles = [f for f in os.listdir('.') if os.path.isfile(f)]
reqFiles = list()
for x in localFiles:
    if os.path.splitext(x)[1] == ".req":
        reqFiles.append(x)

print reqFiles

for index, arg in enumerate(reqFiles):
    print "Processing " + reqFiles[index]
    f = open(reqFiles[index], "r")
    for x in f:
        if x not in pvList:
            pvList.append(x)
            noOfPVs += 1
        

pvList.sort()

if len(sys.argv) > 1:
    if sys.argv[1] in ["-w","-W"]:
        with open('result.txt','w') as f:
            for item in pvList:
                f.write("%s" % item)



if len(sys.argv) > 1:
    if sys.argv[1] in ["-w","-W"]:
        print "req file written to result.txt\n"

