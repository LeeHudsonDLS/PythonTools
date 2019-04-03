import os
import sys
import re
import time


assert len(sys.argv)==2,"Specify a space delimited file containing area and module"
if sys.argv[1] not in  ["-h","-H","--help","-help"]:
    assert os.path.isfile(sys.argv[1]), "File does not exist"
else:
    print ("""Calls dls-svn-git-migrate.sh with contents of specified file.
File must be in the format "area module". For example, ioc BL03I/BL03I-EA-IOC-01""")
    quit()

validAreas = ["support","ioc","python","etc","matlab","tools","epics"]
results = []


qContinue = raw_input("Make sure support module / ioc is checked out in the work area. Continue? y/n\n")

if(qContinue == 'y' or qContinue == 'Y'):
    with open(sys.argv[1],'r') as f:
        for x in f:
            #x.split()
            assert len(x.split())==2,"Requires 2 arguments, the area and the module"
            assert x.split()[0] in validAreas , "Invalid area"
            os.system('echo "y" | dls-svn-git-migrate.sh -a %s'%(x))
            #os.system('echo "y" | python testScript.py -a %s'%(x))
            
    print results
else:
    print("Exiting")  





