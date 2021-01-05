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


FE02I = dict()
FE02I["arch"] = "linux"
FE02I["iocs"] = ["a","b","c"]
#FE02I = {"arch":"Linux","iocs":["FE02I-CS-IOC-01","FE02I-MO-IOC-01","FE02I-ethercat-scanner"],"ethercat":True,"Gauges":["mks937b"]}

feListFile = open(os.path.dirname(__file__)+'/'+"frontEnds.txt","r")
frontEnds = feListFile.read().split()
frontEndData = dict()


for frontEnd in frontEnds:
    data = dict()
    data["iocs"] = list()
    data["ethercat"] = False
    data["arch"] = list()

    CS01 = frontEnd+"-CS-IOC-01"

    # Get a list of all redirector entries for this front end
    redirectorEntries = Popen(f"configure-ioc l | grep {frontEnd}",shell=True,stdout=PIPE).stdout.read().decode().split('\n')

    # Add IOCs to the data dict
    for entry in redirectorEntries:
        # Determine if this front end has ethercat
        if "ethercat" in entry:
            data["ethercat"] = True
        if "CS-IOC-01" in entry:
            CS01_path = entry.split()[1].split('bin')[0]
        try:
            data["iocs"].append(entry.split()[0])
            data["arch"].append(entry.split()[1].split('bin')[1].split('/')[1])
        except:
            pass

    #CS01_path =         

    print("here")















