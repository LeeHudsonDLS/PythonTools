#!/dls_sw/prod/tools/RHEL7-x86_64/defaults/bin/dls-python3
import os
import sys

if len(sys.argv) < 2:
    print("Missing line number")
    quit()

lineToDelete=int(sys.argv[1])

username = os.getlogin()

knownHostsFile = open(f"/home/{username}/.ssh/known_hosts", "r")
contents = knownHostsFile.readlines()
knownHostsFile.close()

knownHostsFile = open(f"/home/{username}/.ssh/known_hosts", "w")

contents.pop(lineToDelete-1)
        
knownHostsFile.writelines(contents)
knownHostsFile.close()
