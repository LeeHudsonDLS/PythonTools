import sys
import os
from subprocess import Popen, PIPE
import argparse

#Just "ls"'s the db directories so you can tell if the ioc is a builder ioc
parser = argparse.ArgumentParser()
parser.parse_args

iocListFile = open("feIOCRedirectorTags.txt","r")
#iocListFile = open("r7SR-VA-IOCS.txt","r")
iocs = iocListFile.read().split()
#ioc = "FE03I-CS-IOC-01"
supportModule = "dlsPLC"
outputList = list()

for ioc in iocs:
    domain = ioc.split('-')[0]
    iocType = ioc.split('-')[1]
    iocNumber = ioc.split('-')[3]


    stdout = Popen(f"configure-ioc s {ioc}",shell=True,stdout=PIPE).stdout.read().decode()
    if(stdout.find("work") == -1):
        workIOC = False;
    else:
        workIOC = True;
    # Determine if the direcory structure is the full version, eg, FE02J/FE02J-CS-IOC-01 or
    # the short version, eg, FE03J/CS
    # If find and rfind (reverse find) come up with the same index is means the ioc name
    # only occurs once which will be in the binary file, this is not the full dir struct
    if (stdout[len(ioc)+1:].find(ioc) == stdout[len(ioc)+1:].rfind(ioc)):
        fullDirStructure = False
    else:
        fullDirStructure = True

    if(fullDirStructure):
        stdout = stdout.split(f"{ioc}")
        iocRelease = stdout[2].split('/')[1]
        if(workIOC):
            baseIOCPath = stdout[1] + ioc + '/'
        else:
            baseIOCPath = stdout[1] + ioc + '/' + iocRelease + '/'
        dbDir = baseIOCPath + "db"

    else:
        stdout = stdout.split(f"{domain}")
        iocRelease = stdout[2].split('/')[2]
        if(workIOC):
            baseIOCPath = stdout[1][len(ioc)-len(domain)+1:] + domain + '/' + iocType + '/'
        else:
            baseIOCPath = stdout[1][len(ioc)-len(domain)+1:] + domain + '/' + iocType + '/' + iocRelease + '/'
        dbDir = baseIOCPath + "db"
        #stdout = Popen(f"configure-ioc s {ioc}",shell=True,stdout=PIPE).stdout.read().decode().split(f"{iocType}")
        #print(stdout)
       
    stdout = Popen(f"ls {dbDir}",shell=True,stdout=PIPE).stdout.read().decode()
    print(f"{ioc}\t\t{stdout}") 
#print(f"{ioc}\t\t{iocRelease}") 
#outputList.append(f"{ioc}\t\t{iocRelease}")

#for a in outputList:
    #print(a)
