import os
import glob
import sys

if len(sys.argv) < 2:
    print "Not enough arguments"
    print "Usage python moduleCheck.py [MAKEIOCS_PATH]"
    print "For example python moduleCheck.py /dls_sw/work/R3.14.12.3/support/BL03I-BUILDER/etc/makeIocs"
    quit()

if sys.argv[1] == "-h" or sys.argv[1] == 'h':
    print "Script determine which modules are used in a builder module"
    print "and which ones of those aren't released in rhel7"
    print "Usage python migrate.py [MAKEIOCS_PATH]"
    print "For example python moduleCheck.py /dls_sw/work/R3.14.12.3/support/BL03I-BUILDER/etc/makeIocs"
    quit()

path = sys.argv[1]
r7Work = "/dls_sw/prod/R3.14.12.7/support"
releaseFiles = list()
usedModules = list()
moduleToMigrate = list()

os.chdir(path)

for file in glob.glob("*_RELEASE"):
    releaseFiles.append(file)



for file in releaseFiles:
    f = open(file,"r")
    for line in f:
        if "$(SUPPORT)" in line or "$(WORK)" in line:
            if line.split('/')[1] not in usedModules:
                usedModules.append(line.split('/')[1])

usedModules.sort()

for module in usedModules:
    if module not in os.listdir(r7Work):
        moduleToMigrate.append(module)

print "Module used: "
for a in usedModules:
    print a

print "\n\nModule to migrate: "
for a in moduleToMigrate:
    print a
