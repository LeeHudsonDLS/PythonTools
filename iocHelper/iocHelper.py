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


workLocation = "/dls_sw/work/R3.14.12.7/support/"

def printData(tableData):

    arch = ''
    if args.linux:
        arch = 'Linux'
    if args.vxworks:
        arch = 'vxWorks'

    for header, row in zip(tableData,tableData):
        if len(arch) > 1:
            if arch in row:
                print(rowFormat.format("",*row))
        else:
            print(rowFormat.format("",*row))

# Return a dict with builder IOC names as key and source builder release as value
# builderIOCS[ioc][0] = builderReleaseFile
# builderIOCS[ioc][1] = iocArch
# builderIOCS[ioc][2] = basePath
# builderIOCS[ioc][3] = release

def getBuilderIOCS():
    feBuilderPath = "/dls_sw/work/R3.14.12.7/support/FE-BUILDER/etc/makeIocs"
    builderIOCs = dict()
    allBuilderIOCs = Popen(f"ls {feBuilderPath} | grep xml",shell=True,stdout=PIPE).stdout.read().decode().replace(".xml","").split('\n')
    allBuilderIOCs.pop()


    for ioc in allBuilderIOCs:
        try:
            iocBootScriptPath = Popen(f"configure-ioc s {ioc}",shell=True,stdout=PIPE).stdout.read().decode().split(" ")[1].strip('\n')
            builderReleaseFile = Popen(f'cat {iocBootScriptPath} | grep "source:"',shell=True,stdout=PIPE).stdout.read().decode().split(' ')[2]
            builderReleaseFile = builderReleaseFile.strip('\n')
            builderReleaseFile = builderReleaseFile.replace(".xml","_RELEASE")
            builderIOCs[ioc] = list()
            builderIOCs[ioc].append(builderReleaseFile)

            if iocBootScriptPath.find('linux') > -1:
                iocArch = "Linux"
            else:
                iocArch = "vxWorks"
            builderIOCs[ioc].append(iocArch)

            basePath = iocBootScriptPath.split("bin")[0]
            builderIOCs[ioc].append(basePath)

            if(basePath.find("work") == -1):
                builderIOCs[ioc].append(basePath.split('/')[-2])
            else:
                builderIOCs[ioc].append("work")

        except:
            print(f"{ioc} not configured")

    return builderIOCs

# Method to get module versions 
def listModulerVersions(iocListFileName,supportModule,latestRelease):
    iocListFile = open(os.path.dirname(__file__)+'/'+iocListFileName,"r")
    iocs = iocListFile.read().split()
    finalOutputList = list()

    builderIOCS = getBuilderIOCS()

    for ioc in iocs:
        domain = ioc.split('-')[0]
        iocType = ioc.split('-')[1]
        iocNumber = ioc.split('-')[3]
        outputList = list()
        FEDep = False
        feMasterConfigDep = False
        FERelease = ""
        if ioc not in builderIOCS.keys():
            builder = False
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

                if stdout.find('linux') > -1:
                    iocArch = "Linux"
                else:
                    iocArch = "vxWorks"

                stdout = stdout.split(f"{ioc}")
                if(workIOC):
                    iocRelease = "work"
                else:
                    iocRelease = stdout[2].split('/')[1]
                
                
                if(workIOC):
                    baseIOCPath = stdout[1] + ioc + '/'
                else:
                    baseIOCPath = stdout[1] + ioc + '/' + iocRelease + '/'
                releaseFile = baseIOCPath + "configure/RELEASE"

            else:
                stdout = stdout.split(f"{domain}")
                if(workIOC):
                    iocRelease = "work"
                    iocArch = stdout[2].split('/')[3][0:7]
                else:
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
        else:
            builder = True
            releaseFile = builderIOCS[ioc][0]
            iocArch = builderIOCS[ioc][1]
            iocRelease = builderIOCS[ioc][3]
        # If we are to use the work version of the ioc modify the release file accordingly.
        if args.work and not workIOC:
            if not builder:
                releaseFile = releaseFile.replace("prod","work")
                releaseFile = releaseFile.replace(f"/{iocRelease}","")
                iocRelease = "work"
            else:
                releaseFile = f"{workLocation}{args.area}-BUILDER/etc/makeIocs/{ioc}_RELEASE"
                iocRelease = "work"

        #Check if using feMasterConfig
        #If using feMasterConfig we must look here for the release file, not in the IOC
        #List all includes that contain feMasterConfig (should be 2)
        stdout = Popen(f"cat {releaseFile} | grep ^[^#] | grep MasterConfig",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
        if stdout[0].find('MasterConfig') != -1:
            feMasterConfigDep = True

        stdout = Popen(f"cat {releaseFile} | grep ^[^#] | grep /FE/",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
        if stdout[0].find('FE') != -1:
            FEDep = True

        if not feMasterConfigDep and not FEDep:
            stdout = Popen(f"cat {releaseFile} | grep ^[^#] | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('/')
            supportModuleRelease = stdout[-1].strip('\n')
            masterConfigRelease = 'N/A'
        elif FEDep:
            stdout = Popen(f"cat {releaseFile} | grep ^[^#] | grep -e /FE/ -e FE=",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
            if stdout[0].find("work") == -1:
                if builder:
                    FERelease = stdout[0].split('/')[-1]
                else:
                    FERelease = stdout[1].split('/')[-3]
            else:
                FERelease = "work"
            
   

            if builder:
                
                commonReleaseFile = f"/dls_sw/prod/R3.14.12.7/support/FE/{FERelease}/configure/RELEASE"
                if stdout.__len__() > 2:
                    platformReleaseFile = stdout[stdout.__len__()-2].replace("include ","")
            else:
                commonReleaseFile = stdout[1].replace("include ","")
                platformReleaseFile = stdout[2].replace("include ","")


            masterConfigRelease = FERelease
            commonReleaseFileCont = Popen(f"cat {commonReleaseFile} | grep ^[^#] | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('/')

            
            if len(platformReleaseFile) > 1:
                platformReleaseFileCont = Popen(f"cat {platformReleaseFile} | grep ^[^#] | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('/')
            else:
                platformReleaseFileCont = ""

            if  len(commonReleaseFileCont) > 1:
                supportModuleRelease = commonReleaseFileCont[-1].strip('\n')
            else:
                supportModuleRelease = platformReleaseFileCont[-1].strip('\n')

        elif feMasterConfigDep:
            stdout = Popen(f"cat {releaseFile} | grep ^[^#] | grep MasterConfig",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
            if stdout[0].find("work") == -1:
                masterConfigRelease = stdout[0].split('/')[-3]
            else:
                masterConfigRelease = "work"
            
            commonReleaseFile = stdout[0].replace("include ","")
            commonReleaseFileCont = Popen(f"cat {commonReleaseFile} | grep ^[^#] | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('/')
            
            platformReleaseFile = stdout[1].replace("include ","")
            if len(platformReleaseFile) > 1:
                platformReleaseFileCont = Popen(f"cat {platformReleaseFile} | grep ^[^#] | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('/')
            else:
                platformReleaseFileCont = ""

            if  len(commonReleaseFileCont) > 1:
                supportModuleRelease = commonReleaseFileCont[-1].strip('\n')
            else:
                supportModuleRelease = platformReleaseFileCont[-1].strip('\n')


        # Check if the module is actually used in this IOC:
        #print(f"{ioc}")

        #if ioc not in builderIOCS.keys():
            #stdout = Popen(f"cat {baseIOCPath}db/{ioc}.db | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode()
        #else:
            #stdout = Popen(f"cat {builderIOCS[ioc][2]}db/{ioc}_expanded.db | grep {supportModule}",shell=True,stdout=PIPE).stdout.read().decode()

        #if(len(stdout)==0):
            #supportModuleRelease = ''


        outputList.append(f"{ioc}")
        outputList.append(f"{iocRelease}")
        outputList.append(f"{iocArch}")
        outputList.append(f"{masterConfigRelease}")
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
parser.add_argument('-l','--linux',action='store_true')
parser.add_argument('-v','--vxworks',action='store_true')
parser.add_argument('-w','--work',action='store_true')
parser.add_argument("supportModule",nargs='?', help="String describing which support module you want to search for", default="digitelMpc")
args=parser.parse_args()

validRhelVersions = [0,6,7]
validAreas = ["FE","SR","BR","A"]
print(f"Finding latest releases of {args.supportModule}")

# Get the support module latest release using ls
latestR6Release = Popen(f"ls -tr /dls_sw/prod/R3.14.12.3/support/{args.supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
while latestR6Release[-2].find("tar") > -1:
    latestR6Release.pop()
latestR6Release = latestR6Release[-2]

latestR7Release = Popen(f"ls -tr /dls_sw/prod/R3.14.12.7/support/{args.supportModule}",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
while latestR7Release[-2].find("tar") > -1:
    latestR7Release.pop()
latestR7Release = latestR7Release[-2]

print(f"Latest R3.14.12.3 release of {args.supportModule} is {latestR6Release}")
print(f"Latest R3.14.12.7 release of {args.supportModule} is {latestR7Release}")
iocListFileName = ""

tableHeader = ["IOC","IOC Release","IOC Arch","masterConfig","Support Module","EPICS","Current","Latest"]
rowFormat = "{}"
rowFormat += "{:<20}{:<16}{:<12}{:<18}{:<20}{:<15}{:<16}{:<16}"
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
            printData(tableData)
            quit()
            
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

printData(tableData)













