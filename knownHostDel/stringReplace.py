#!/dls_sw/prod/tools/RHEL7-x86_64/defaults/bin/dls-python3
import os
import sys
from subprocess import Popen, PIPE

original = str(sys.argv[1])
new = str(sys.argv[2])

cmd = f'grep -lr "{original}" {os.getcwd()}'

files = Popen(cmd,shell=True,stdout=PIPE).stdout.read().decode().split()

for fileName in files:
    file = open(fileName, "r")
    contents = file.readlines()
    for i,line in enumerate(contents):
        contents[i]=line.replace(original,new)
    file.close()


    file = open(fileName, "w")            
    file.writelines(contents)
    file.close()
