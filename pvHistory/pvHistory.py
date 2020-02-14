
import sys
import datetime

from subprocess import Popen, PIPE
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("pvName", help="Name of the PV")
parser.add_argument("-a","--all",action="store_true", help="Show all instances of PV in save files, not just changes")
parser.add_argument("-y","--year",nargs=1, help="Limit search to a particular year, eg 2019")
args = parser.parse_args()


def getDate(fileName: str)-> str:

    # If filename has a date at the end
    if(len(fileName.split('_'))==3):

        # Get the unformatted TIME part of the filename
        timeFragment = fileName.split('-')[-1]

        # Get the unformatted DATE part of the filename
        dateFragment = fileName.split('-')[-2:-1][0].split('_')[-1]

        # Format date and time
        date =(f'20{dateFragment[:2]}-{dateFragment[-4:-2]}-{dateFragment[-2:]}')
        time =(f'{timeFragment[0:2]}:{timeFragment[2:4]}:{timeFragment[4:6]}')
        return f'{date}__{time}'
    else:
        return 'Today'


now = datetime.datetime.now()

if(args.year):
    assert(int(args.year[0])>2000 and int(args.year[0]) <= now.year)
    year = int(str(args.year[0])[-2:])
else:
    year = int(str(now.year)[-2:])



pvName = args.pvName
values = list(list())
values2 = list()
changed = list()

# Get autosave file names from the chosen year and sort them
stdout = Popen(f"grep -nr '{pvName}'", shell=True, stdout=PIPE).stdout

#Go through each file and grep for the PV
for i in stdout:
    fileName = i.decode().rstrip("\n").split(':')[0]
    value = i.decode().rstrip("\n").split(' ')[-1]
    if('#' not in i.decode()):
        values.append((fileName,value))



for a in values:
    values2.append(str(getDate(a[0]))+"     "+a[1])

values2.sort()


oldValue = 0.0
for a in values2:
    currentValue = float(a.split(' ')[-1])
    if(currentValue!=oldValue):
        changed.append(a)
        oldValue=currentValue

if(args.all):
    for a in values2:
        if(a[2:4].isdigit()):
            if(int(a[2:4])==year or not args.year):
                print(a)
        else:
            print(a)
else:
    for a in changed:
        if(a[2:4].isdigit()):
            if(int(a[2:4])==year or not args.year):
                print(a)
        else:
            print(a)