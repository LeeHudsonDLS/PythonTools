#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse

#Nasty script to tell what version of a support module is running in all the iocs listed in iocs.txt
parser = argparse.ArgumentParser()
parser.add_argument("rhelVers", nargs='?', help="Int describing which RHEL version the IOCs was built with: 6,7", default=7)
parser.add_argument("area",nargs='?', help="String describing which area of IOCs you want to search: FE,SR", default="FE")
parser.add_argument("supportModule",nargs='?', help="String describing which support module you want to search for", default="FE")
args=parser.parse_args()

validRhelVersions = [6,7]
validAreas = ["FE","SR"]

iocListFileName = ""

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
else:
    print(f"Invalid area, must be in {validAreas}")
    quit()


iocListFile = open(iocListFileName,"r")
iocs = iocListFile.read().split()
supportModule = args.supportModule
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
        #stdout = Popen(f"configure-ioc s {ioc}",shell=True,stdout=PIPE).stdout.read().decode().split(f"{iocType}")
        #print(stdout)
       
    stdout = Popen(f"cat {releaseFile} | grep ^[^#] | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('/')
    supportModuleRelease = stdout[-1]
    #print(f"{ioc}\t\t{supportModule}\t{supportModuleRelease}\t{releaseFile[1:]}") 
    print(f"{ioc}\t\t{supportModule}\t{supportModuleRelease}") 
    #print(f"{ioc}\t\t{iocRelease}") 
    #outputList.append(f"{ioc}\t\t{iocRelease}")

#for a in outputList:
    #print(a)
