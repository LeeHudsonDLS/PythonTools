#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse
import fileinput


# Method to get module versions 
def listModulerVersions(iocListFileName,vers):
    iocListFile = open(os.path.dirname(__file__)+'/'+iocListFileName,"r")

    if(args.ioc == 'A'):
        iocs = iocListFile.read().split()
    else:
        iocs =[args.ioc]

    builderIOCS=['FE10B-CS-IOC-01']
    for ioc in iocs:
        # Skip commented out IOC
        if(ioc[0]=='#'):
            continue

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
            Popen(f"rm {releaseFile}.temp",shell=True,stdout=PIPE,stderr=PIPE)
        
        releaseFileContents = Popen(f"cat {releaseFile}",shell=True,stdout=PIPE).stdout.read().decode()

        # Print release file
        if(args.print):
            print(f"{releaseFile}:")
            #print(len(releaseFileContents.split("\n")))
            #print(f"\t{releaseFileContents}")
            for line in releaseFileContents.split('\n'):
                print(f"\t{line}")
            #print(f"\t{archRelease}")
        else:
            fin = open(releaseFile, "rt")
            fout = open(f"{releaseFile}.temp", "wt")
            if vers == "work" or vers == "w":
                for line in fin:
                    if line.find('prod') > -1 or line.find('SUPPORT') > -1:
                        releaseStart=line.find('/',line.find("FE",3))+1
                        if line.find('/',releaseStart) > -1:
                            releaseEnd = line.find('/',releaseStart)
                        else:
                            releaseEnd = line.find('\n',releaseStart)
                        
                        
                        releaseStr = "/"+line[releaseStart:releaseEnd]

                        output = line.replace('prod','work')
                        output = output.replace('SUPPORT','WORK')
                        output = output.replace(releaseStr, '')
                        fout.write(output)
            else:
                for line in fin:
                    if line.find('prod') > -1 or line.find('SUPPORT') > -1:
                        releaseStart=line.find('/',line.find("FE",3))+1
                        if line.find('/',releaseStart) > -1:
                            releaseEnd = line.find('/',releaseStart)
                        else:
                            releaseEnd = line.find('\n',releaseStart)
                        
                        
                        releaseStr = line[releaseStart:releaseEnd]
                        output = line.replace(releaseStr, vers)
                        output = output.replace('//','/')
                        fout.write(output)
                    else:
                        output = line.replace('work','prod')
                        output = output.replace('WORK','SUPPORT')
                        output = output.replace("/FE","/FE/"+vers)
                        fout.write(output)
                        
 
            fin.close()
            fout.close()
            Popen(f"mv {releaseFile}.temp {releaseFile}",shell=True,stdout=PIPE)

            
            


parser = argparse.ArgumentParser()
parser.add_argument("vers", nargs='?',help="Version of feMasterConfig to update to")
parser.add_argument('-p','--print',action='store_true',help="Just print the current trimmed down RELEASE file")
parser.add_argument('-i',dest="ioc",nargs='?', help="If you only want to change a single IOC, use this argument with the IOC name", default="A")

args=parser.parse_args()

if args.vers == None and args.print == False:
    print("Please specify the version of feMasterConfig")
    quit()


print(os.path.dirname(__file__))
if(args.print):
    print("Printing WORK release file contents")
listModulerVersions("iocs.txt",args.vers)
