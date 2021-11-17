#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("valve",nargs='?', help="String describing the base PV for the valve, eg FE15I-VA-VALVE-01", default="FE15I-VA-VALVE-01")
parser.add_argument('-a','--all',action='store_true')

args=parser.parse_args()
dom = args.valve.split('-')[0]
output = ""
feArea = args.valve.split('-')[0].replace("FE",'')

if args.all:
    valvePVs = [f"{dom}-RS-ABSB-01",f"{dom}-VA-VALVE-01",f"{dom}-VA-VALVE-02",f"{dom}-VA-FVALV-01",f"{dom}-PS-SHTR-01",f"{dom}-PS-SHTR-02",f"{dom}-MP-PERMT-01"]
else:
    valvePVs=args.valve

for device in valvePVs:
    valve = dict()

    builderClasses={"FE.absorber_1_sub":"ABSB-01",
                    "FE.valve_1_sub":"VALVE-01",
                    "FE.valve_2_sub":"VALVE-02",
                    "FE.fvalv_1_sub":"FVALV-01",
                    "FE.shtr_1_sub":"SHTR-01",
                    "FE.shtr_2_sub":"SHTR-02",
                    "FE.mps_permit_sub":"PERMT-01"
    }

    # Get the main builder class
    for key, value in builderClasses.items():
        if value in device:
            builderClass = key


    #valve["FE_AREA"]=args.valve.split('-')[0]

    for val in range(0,16):
        valve[f"ILK{val}"] = ""
        if "mps" not in builderClass: 
            valve[f"GILK{val}"] = ""



    for key in valve:
        val = Popen(f"caget {device}:{key}",shell=True,stdout=PIPE).stdout.read().decode()
        try:
            valve[key]=val.replace(val.split()[0],"").strip()
        except:
            valve[key]=""

    # Print xml
    output += f"<{builderClass} "
    output += f'FE_AREA="{feArea}" '
    for key, value in valve.items():
        output+= f'{key}="{value}" '
    output += "/>"
    output += '\r\n'

output = output.replace('&',"&amp;amp;")

# Builder bug?
output = output.replace(')','')
print(output)

        

