#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("file",nargs='?', help="Which template file in the sub are you looking for?", default="mks937a.template")
args=parser.parse_args()


getIOCPathString = "configure-ioc list | grep ^SR[0-2][0-9]C-VA-IOC-01 | grep vxWorks"

iocSubFileList = list()

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

    for line in lines:
        if foundFile:
            if line[0] != '#':
                fileInstance += line
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
    print(fileInstance)
        
