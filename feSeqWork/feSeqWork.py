#!/usr/bin/env dls-python3

from ast import arg
from subprocess import Popen, PIPE
import os
import sys

# Simple script for changing between the version of dls_feSequencer specified by the redirector (feSequencer)
# and the latest release. This should be done in the root of the python IOC in question

if len(sys.argv) > 1:
    if sys.argv[1]== "w":
        path = Popen(f"configure-ioc s feSequencer",shell=True,stdout=PIPE).stdout.read().decode().split()[1]
        os.system(f'pipenv install -e {path} --skip-lock')
    else:
        os.system("pipenv uninstall dls-fesequencer")
        os.system("pipenv install dls-fesequencer")
else:
    print("Choose w or p for work or prod")
