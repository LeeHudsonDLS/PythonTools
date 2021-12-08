#!/bin/env dls-python3

import sys
import re
from subprocess import Popen, PIPE
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("file",nargs='?', help="Which template file in the sub are you looking for?", default="mks937a.template")
args=parser.parse_args()


getIOCPathString = "configure-ioc list | grep ^SR[0-2][0-9]C-VA-IOC-01 | grep vxWorks"

iocSubFileList = list()
commonality = dict()
fileInstanceList = dict()
fileInstanceListRaw = dict()

# Get list of substitution files
for redirectorOp in Popen(getIOCPathString,shell=True,stdout=PIPE).stdout.read().decode().split('\n'):
    try:
        ioc = redirectorOp.split()[0]
        path = redirectorOp.split()[1].split("bin/")[0]
        iocSubFileList.append(f"{path}{ioc}App/Db/{ioc}.substitutions")
    except:
        pass

for sub in iocSubFileList:
    substitutionFile = open(sub,'r')
    lines = substitutionFile.readlines()
    foundFile = False

    fileInstance = ""
    openBracketCounter = 0
    closedBracketCounter = 0
    prefix = ""

    for line in lines:
        if foundFile:
            if line[0] != '#':
                fileInstance += line
                if len(prefix) < 1:
                    reResult = re.compile("SR[0-2][0-9]").findall(line)
                    if len(reResult) > 0:
                        prefix = reResult[0]
        if f"file {args.file}" in line and not foundFile:
            foundFile = True
            fileInstance += line
        if foundFile:
            if '{' in line:
                openBracketCounter += 1
            if '}' in line:
                closedBracketCounter += 1
        if openBracketCounter > 0 and openBracketCounter == closedBracketCounter:
            foundFile = False
            openBracketCounter = 0
            closedBracketCounter = 0
    
    fileInstance = fileInstance.replace(prefix,"SRxx")
    fileInstanceList[prefix]=fileInstance
    fileInstanceListRaw[prefix]=fileInstance.replace(' ','').replace('\r','').replace('\n','').replace('\t','')

# Create a dict as follows:
# {<rawSubstitutionText>:<list of cells that have this exact text>} eg:
# {rawSubstitutionText:[SR01,SR02,SR03]}
for fi in fileInstanceListRaw:
    fileInstanceText = fileInstanceListRaw[fi]
    if fileInstanceText in commonality:
        commonality[fileInstanceText].append(fi)
    else:
        commonality[fileInstanceText]=list()
        commonality[fileInstanceText].append(fi)




for config in commonality:
    cells = ""
    cell=commonality[config][0]
    for cell in commonality[config]:
        cells += f"{cell} "
    cells += ':'
    print(cells)
    print(fileInstanceList[cell])
        
