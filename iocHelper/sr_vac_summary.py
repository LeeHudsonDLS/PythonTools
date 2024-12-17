#!/bin/env dls-python3

import sys
import os
from subprocess import Popen, PIPE
import argparse


class SRSummaryChecker:

    def __init__(self):
        self.builderRoot = "/dls_sw/work/R3.14.12.7/support/SR-BUILDER/etc/makeIocs"
        self.builderIOCs = [f'SR{cell}C' for cell in range(0,25)]
        print("test")


    def getInstanceInXML(self,targetString):

        result = Popen(f"cat {self.builderRoot}",shell=True,stdout=PIPE).stdout.read().decode().split(" ")[1].strip('\n')


