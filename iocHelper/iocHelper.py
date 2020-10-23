#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse

def listModulerVersions(iocListFileName,supportModule):
    iocListFile = open(os.path.dirname(__file__)+'/'+iocListFileName,"r")
    iocs = iocListFile.read().split()
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
            releaseFile = baseIOCPath + "configure/RELEASE"

        else:
            stdout = stdout.split(f"{domain}")
            iocRelease = stdout[2].split('/')[2]
            if(workIOC):
                baseIOCPath = stdout[1][len(ioc)-len(domain)+1:] + domain + '/' + iocType + '/'
            else:
                baseIOCPath = stdout[1][len(ioc)-len(domain)+1:] + domain + '/' + iocType + '/' + iocRelease + '/'
            releaseFile = baseIOCPath + "configure/RELEASE"
        
        epicsVersion = baseIOCPath.split('/')[3]   
        stdout = Popen(f"cat {releaseFile} | grep ^[^#] | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('/')
        supportModuleRelease = stdout[-1].strip('\n')
        print(f"{ioc}\t\t{iocRelease}\t\t{supportModule}\t{epicsVersion}\t{supportModuleRelease}") 

#Nasty script to tell what version of a support module is running in all the iocs listed in iocs.txt
parser = argparse.ArgumentParser()
parser.add_argument('-r',dest="rhelVers", nargs='?', help="Int describing which RHEL version the IOCs was built with: 6,7", default=0)
parser.add_argument('-a',dest="area",nargs='?', help="String describing which area of IOCs you want to search: FE,SR,BR", default="A")
parser.add_argument("supportModule",nargs='?', help="String describing which support module you want to search for", default="mks937b")
args=parser.parse_args()

validRhelVersions = [0,6,7]
validAreas = ["FE","SR","BR","A"]

iocListFileName = ""

if(int(args.rhelVers) > 0):
    if(int(args.rhelVers) in validRhelVersions):
        iocListFileName += f"r{args.rhelVers}"
    else:
        print(f"Invalid rhelVers, must be in {validRhelVersions}")
        quit()

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
                listModulerVersions(iocListFileName,args.supportModule)
            quit()
            
    else:
        print(f"Invalid area, must be in {validAreas}")
        quit()

    listModulerVersions(iocListFileName,args.supportModule)

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
        listModulerVersions(iocListFileName,args.supportModule)














