#!/bin/env dls-python3

import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file",nargs='?', help="Full file path", default="/scratch/FE14I/FE14I-CS-IOC-01/FE14I-CS-IOC-01App/Db/fe.vm")
args=parser.parse_args()


def createPatternList(patternLine):
    patternRaw = patternLine.split()
    patternRaw = list(dict.fromkeys(patternRaw))
    try:
        patternRaw.remove("pattern")
    except:
        pass
    try:
        patternRaw.remove("{")
    except:
        pass
    try:
        patternRaw.remove(",")
    except:
        pass
    try:
        patternRaw.remove("}")
    except:
        pass
    patternRaw = [pat.replace(',','') for pat in patternRaw]
    patternRaw = [pat.replace('"','') for pat in patternRaw]
    return patternRaw

def createInstanceList(patternLine):
    patternRaw = patternLine.split(',')

    patternRaw = [pat.replace('{','') for pat in patternRaw]
    patternRaw = [pat.replace('}','') for pat in patternRaw]
    patternRaw = [pat.replace('\n','') for pat in patternRaw]
    patternRaw = [re.sub("\s\s+" , " ", pat) for pat in patternRaw]
    patternRaw = [pat.replace(',','') for pat in patternRaw]
    patternRaw = [pat.replace('"','') for pat in patternRaw]
    patternRaw = [pat.strip() for pat in patternRaw]
    return patternRaw


file = open(args.file,'r')
lines = file.readlines()

inPattern = False

for line in lines:
    if line[0] == '}':
        inPattern = False
    if "pattern" in line:
        inPattern = True
        pattern = createPatternList(line)
    elif inPattern:
        instance = createInstanceList(line)
        xml="<"
        for pat, inst in zip(pattern,instance):
            xml+=f'{pat}="{inst}" '
        xml+="/>"
        print(xml)
        print("")






