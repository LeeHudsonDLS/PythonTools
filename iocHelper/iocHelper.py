#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Method to get module versions 
def listModulerVersions(iocListFileName,supportModule,latestRelease):
    iocListFile = open(os.path.dirname(__file__)+'/'+iocListFileName,"r")
    iocs = iocListFile.read().split()
    finalOutputList = list()

    for ioc in iocs:
        domain = ioc.split('-')[0]
        iocType = ioc.split('-')[1]
        iocNumber = ioc.split('-')[3]
        outputList = list()


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

        # Fudge for FE02I that has DDBA in the boot script name
        if(ioc == "FE02I-CS-IOC-01"):
            fullDirStructure = True

        if(fullDirStructure):
            stdout = stdout.split(f"{ioc}")
            iocRelease = stdout[2].split('/')[1]
            iocArch = stdout[2].split('/')[3][0:7]
            aa = iocArch.find('linux')
            if iocArch.find('linux') > -1:
                iocArch = "Linux"
            if(workIOC):
                baseIOCPath = stdout[1] + ioc + '/'
            else:
                baseIOCPath = stdout[1] + ioc + '/' + iocRelease + '/'
            releaseFile = baseIOCPath + "configure/RELEASE"

        else:
            stdout = stdout.split(f"{domain}")
            iocRelease = stdout[2].split('/')[2]
            iocArch = stdout[2].split('/')[4][0:7]
            if iocArch.find('linux') > -1:
                iocArch = "Linux"
            if(workIOC):
                baseIOCPath = stdout[1][len(ioc)-len(domain)+1:] + domain + '/' + iocType + '/'
            else:
                baseIOCPath = stdout[1][len(ioc)-len(domain)+1:] + domain + '/' + iocType + '/' + iocRelease + '/'
            releaseFile = baseIOCPath + "configure/RELEASE"
        
        epicsVersion = baseIOCPath.split('/')[3]
        stdout = Popen(f"cat {releaseFile} | grep ^[^#] | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('/')
        supportModuleRelease = stdout[-1].strip('\n')
        outputList.append(f"{ioc}")
        outputList.append(f"{iocRelease}")
        outputList.append(f"{iocArch}")
        outputList.append(f"{supportModule}")
        outputList.append(f"{epicsVersion}")
        outputList.append(f"{supportModuleRelease}")
        outputList.append(f"{latestRelease}")

        finalOutputList.append(outputList)
    return finalOutputList

#Nasty script to tell what version of a support module is running in all the iocs listed in iocs.txt
parser = argparse.ArgumentParser()
parser.add_argument('-r',dest="rhelVers", nargs='?', help="Int describing which RHEL version the IOCs was built with: 6,7", default=7)
parser.add_argument('-a',dest="area",nargs='?', help="String describing which area of IOCs you want to search: FE,SR,BR", default="A")
parser.add_argument("supportModule",nargs='?', help="String describing which support module you want to search for", default="mks937b")
args=parser.parse_args()

validRhelVersions = [0,6,7]
validAreas = ["FE","SR","BR","A"]
print(f"Finding latest releases of {args.supportModule}")

# Get the support module latest release using dls-list-releases.py
latestR6Release = Popen(f"dls-list-releases.py -e R3.14.12.3 -l {args.supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('\n')[0]
latestR7Release = Popen(f"dls-list-releases.py -e R3.14.12.7 -l {args.supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('\n')[0]
#latestR6Release="2-86-1"
#latestR7Release="2-87"
print(f"Latest R3.14.12.3 release of {args.supportModule} is {latestR6Release}")
print(f"Latest R3.14.12.7 release of {args.supportModule} is {latestR7Release}")
iocListFileName = ""

tableHeader = ["IOC","IOC Release","IOC Arch","Support Module","EPICS","Current","Latest"]
rowFormat = "{}"
rowFormat += "{:<20}{:<16}{:<16}{:<20}{:<15}{:<16}{:<16}"
tableData = list()
print(rowFormat.format("",*tableHeader))
#print(f"IOC\t\t\tIOC Release\tSupport Module\tEPICS\t\tCurrent\tLatest") 


if(int(args.rhelVers) > 0):
    if(int(args.rhelVers) in validRhelVersions):
        iocListFileName += f"r{args.rhelVers}"
    else:
        print(f"Invalid rhelVers, must be in {validRhelVersions}")
        quit()
    if(args.rhelVers == '6'):
        latestRelease = latestR6Release
    else:
        latestRelease = latestR7Release

    if(args.area in validAreas):
        if(args.area == "FE"):
            iocListFileName += "FE-CS-IOCS.txt"
        if(args.area == "SR"):
            iocListFileName += "SR-VA-IOCS.txt"
        if(args.area == "BR"):
            iocListFileName += "BR-VA-IOCS.txt"
        if(args.area == "A"):
            iocListFiles = Popen(f"ls {os.path.dirname(__file__)}/ | grep {iocListFileName} | grep IOCS.txt",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
            for iocListFileName in iocListFiles[:-1]:
                for a in listModulerVersions(iocListFileName,args.supportModule,latestRelease):
                    tableData.append(a)
                    #tableData.append(listModulerVersions(iocListFileName,args.supportModule,latestRelease))
            #quit()
            
    else:
        print(f"Invalid area, must be in {validAreas}")
        quit()

    for a in listModulerVersions(iocListFileName,args.supportModule,latestRelease):
        tableData.append(a)
        #tableData.append(listModulerVersions(iocListFileName,args.supportModule,latestRelease))

else:
    if(args.area in validAreas):
        if(args.area == "FE"):
            iocListFiles = Popen(f"ls {os.path.dirname(__file__)}/ | grep FE-CS-IOCS.txt",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
        if(args.area == "SR"):
            iocListFiles = Popen(f"ls {os.path.dirname(__file__)}/ | grep SR-VA-IOCS.txt",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
        if(args.area == "BR"):
            iocListFiles = Popen(f"ls {os.path.dirname(__file__)}/ | grep BR-VA-IOCS.txt",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
        if(args.area == "A"):
            iocListFiles = Popen(f"ls {os.path.dirname(__file__)}/ | grep IOCS.txt",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
    else:
        print(f"Invalid area, must be in {validAreas}")
        quit()
 
    for iocListFileName in iocListFiles[:-1]:
        if(iocListFileName.find('7') !=-1):
            for a in listModulerVersions(iocListFileName,args.supportModule,latestR7Release):
                tableData.append(a)
                #tableData.append(listModulerVersions(iocListFileName,args.supportModule,latestR7Release))
        else:
            for a in listModulerVersions(iocListFileName,args.supportModule,latestR6Release):
                tableData.append(a)
                #tableData.append(listModulerVersions(iocListFileName,args.supportModule,latestR6Release))

for header, row in zip(tableData,tableData):
    print(rowFormat.format("",*row))













