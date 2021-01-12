#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse
import fileinput


# Method to get module versions 
def listModulerVersions(iocListFileName,vers):
    iocListFile = open(os.path.dirname(__file__)+'/'+iocListFileName,"r")
    iocs = iocListFile.read().split()
    builderIOCS=['FE10B-CS-IOC-01']
    for ioc in iocs:
        domain = ioc.split('-')[0]
        iocType = ioc.split('-')[1]


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
            if iocArch.find('linux') > -1:
                iocArch = "Linux"
            if(workIOC):
                baseIOCPath = stdout[1] + ioc + '/'
            else:
                baseIOCPath = stdout[1] + ioc + '/' + iocRelease + '/'

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
        
        if(ioc in builderIOCS):
            workIOCPath = "/dls_sw/work/R3.14.12.7/support/FE-BUILDER/etc/makeIocs"
            releaseFile = f"{workIOCPath}/{ioc}_RELEASE"
        else:
            # If baseIOCPath begins with whitespace, remove the whitespace
            if baseIOCPath[0]==' ':
                baseIOCPath=baseIOCPath[1:]
            iocRelease = baseIOCPath.split('/')[-2]
            workIOCPath = baseIOCPath.replace(f'{iocRelease}/','')
            workIOCPath = workIOCPath.replace('prod','work')
            releaseFile = workIOCPath + "configure/RELEASE"
        
        releaseFileContents = Popen(f"cat {releaseFile}",shell=True,stdout=PIPE).stdout.read().decode()
        commonRelease = releaseFileContents.split('\n')[1]
        archRelease = releaseFileContents.split('\n')[2]

        

        # Print release file
        if(args.print):
            print(f"{releaseFile}")
            print(f"\t{commonRelease}")
            print(f"\t{archRelease}")
        else:
            if vers == "work" or vers == "w":
                commonRelease = "include /dls_sw/work/R3.14.12.7/support/feMasterConfig/configure/FE_COMMON_RELEASE"
                if iocArch == "Linux":
                    archRelease = "include /dls_sw/work/R3.14.12.7/support/feMasterConfig/configure/FE_LINUX_RELEASE"
                else:
                    archRelease = "include /dls_sw/work/R3.14.12.7/support/feMasterConfig/configure/FE_VXWORKS_RELEASE"
            else:
                commonRelease = f"include /dls_sw/prod/R3.14.12.7/support/feMasterConfig/{vers}/configure/FE_COMMON_RELEASE"
                if iocArch == "Linux":
                    archRelease = f"include /dls_sw/prod/R3.14.12.7/support/feMasterConfig/{vers}/configure/FE_LINUX_RELEASE"
                else:
                    archRelease = f"include /dls_sw/prod/R3.14.12.7/support/feMasterConfig/{vers}/configure/FE_VXWORKS_RELEASE"
            
            for line in fileinput.input(releaseFile,inplace=True):
                if "FE_COMMON" in line:
                    print('{}'.format(commonRelease), end='\n')
                elif "FE_LINUX" in line or "FE_VXWORKS" in line:
                    print('{}'.format(archRelease), end='\n')
                else:
                    print('{}'.format(line), end='')


parser = argparse.ArgumentParser()
parser.add_argument("vers", nargs='?',help="Version of feMasterConfig to update to")
parser.add_argument('-p','--print',action='store_true',help="Just print the current trimmed down RELEASE file")
args=parser.parse_args()

if args.vers == None and args.print == False:
    print("Please specify the version of feMasterConfig")
    quit()


print(os.path.dirname(__file__))
listModulerVersions("iocs.txt",args.vers)