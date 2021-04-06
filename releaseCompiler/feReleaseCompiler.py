#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse



modules = list(list())
modulesUnique = list()
#files = ['SR02C','SR02J','SR05C','SR07B','SR08C','SR10B','SR11K','SR14C','SR21C','SR21B','SR23C','SR24B']
files = ['SR01C','SR03C','SR04C','SR05C','SR06C','SR07C','SR08C','SR09C','SR10C','SR11C','SR12C','SR13C','SR14C','SR15C','SR16C','SR17C','SR18C','SR19C','SR20C','SR21C','SR22C','SR23C','SR24C']


for file in files:
    if len(file) > 0:
        releaseFile = open(f"{file}_RELEASE","r")
        for line in releaseFile:
            if line[0] != '#' and line[0].isspace() != True:
                macro = line.split('/')[0]
                module = line.split('/')[1]
                if module not in modulesUnique:
                    moduleCnfo = list()
                    moduleCnfo.append(macro)
                    moduleCnfo.append(module)
                    moduleCnfo.append(file)
                    modules.append(moduleCnfo)
                    modulesUnique.append(module)

for a in modules:
    print(a)







