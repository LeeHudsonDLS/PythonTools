#!/dls_sw/prod/tools/RHEL7-x86_64/defaults/bin/dls-python3
import os
import sys
import glob
from shutil import copyfile

# arg[1] autosave directory

if len(sys.argv) < 2:
    print("Not enough arguments")
    print("Usage python migrate.py [AUTOSAVE_PATH]")
    print("For example python migrate.py /dls_sw/i04/epics/autosave/BL04I-VA-IOC-01")
    quit()

if len(sys.argv[1]) < 3:
    if sys.argv[1] == "-h" or sys.argv[1] == h:
        print("Script to copy old spreadsheet style autosave files to builder format")
        print("For example, copy BL04I_2.sav2 to BL04I-MO-IOC-06_2.sav2")
        print("Usage python migrate.py [AUTOSAVE_PATH]")
        print("For example python migrate.py /dls_sw/i04/epics/autosave/BL04I-VA-IOC-01")
    quit()



# Get the first argument and split it like a path
argument = sys.argv[1].split('/')



# Find the part of the argument that specifies IOC name
for a in argument:
    if a[:2] == "BL" or "FE" or "BR" or "SR":
        IOC = a

fileExtensions=["*.sav","*.sav0","*.sav1","*.sav2","*.savB"]
originalFile = list()
newFile = list()

os.chdir(sys.argv[1])

# Iterate through the list of file extension, for every file with that extension
# copy the file but replace the beamline characters (BL04I) for example with
# the IOC name, so BL04I_0.sav0 is copied to BL04I-MO-IOC-01_0.sav0
for extension in fileExtensions:
    debugGlob = glob.glob(extension)
    for file in glob.glob(extension):
        if IOC in file:
            # Check if the migration has already been performed
            print(f"{file} already exists")
            quit()
        originalFile.append(file)


for file in originalFile:
        copyfile(file,file.replace(file[:5],IOC))


