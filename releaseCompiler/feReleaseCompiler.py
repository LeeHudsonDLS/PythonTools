#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse



modules = list(list())
modulesUnique = list()
#files = ['FE02I','FE02J','FE05I','FE07B','FE08I','FE10B','FE11K','FE14I','FE21I','FE21B','FE23I','FE24B']
files = ['FE03I','FE04I','FE06I','FE07I','FE09I','FE10I','FE11I','FE12I','FE13I','FE15I','FE16I','FE16B','FE18I','FE18B','FE19I','FE20I','FE22I','FE22B','FE23B','FE24I']
#files = Popen(f"ls | grep _RELEASE",shell=True,stdout=PIPE).stdout.read().decode().split('\n')
#print(files)

for file in files:
    if len(file) > 0:
        releaseFile = open(f"{file}_RELEASE","r")
        for line in releaseFile:
            if line[0] != '#' and line[0].isspace() != True:
                macro = line.split('/')[0]
                module = line.split('/')[1]
                if module not in modulesUnique:
                    moduleInfo = list()
                    moduleInfo.append(macro)
                    moduleInfo.append(module)
                    moduleInfo.append(file)
                    modules.append(moduleInfo)
                    modulesUnique.append(module)

for a in modules:
    print(a)







