from cothread import *
from cothread.catools import caput, caget, caget_array
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class girderPositionHelper:
    def __init__(self):
        self.cellPrefix = [f'SR{cell:02d}A' for cell in range(1,25)]
        self.cellPrefix.remove('SR02A')
        self.disconnectedPVs = list()

    
    def triggerLoad(self):
        for cell in self.cellPrefix:
            try:
                caput(f'{cell}-AL-SERVC-01:INITLOADALL.PROC',1,timeout=1)
            except Exception as e:
                missingPv = str(e).split()[0][0:-1]
                self.disconnectedPVs.append(missingPv)
                print(f"{missingPv} not connected")

    def getAllLoaded(self):
        for cell in self.cellPrefix:
            try:
                loaded = caget_array([f'{cell}-AL-RENC-{enc:02d}:HADLOAD' for enc in range(1,16)],datatype=str)
                loaded = [l[0:3] for l in loaded]

                if len(set(loaded)) == 1 and loaded[0] == 'Yes':
                    print(f'{bcolors.OKGREEN}{cell}:{loaded}{bcolors.ENDC}')
                else:
                    print(f'{bcolors.FAIL}{cell}{bcolors.ENDC}:[', end='')
                    for l in loaded:
                        if l != 'Yes':
                            print(f"{bcolors.FAIL}'{l}'{bcolors.ENDC}, ", end='')
                        else:
                            print(f"{bcolors.OKGREEN}'{l}'{bcolors.ENDC}, ", end='')
                    print()
            except Exception as e:
                print(f'{bcolors.WARNING}{str(e)}{bcolors.ENDC}')


    # Method gets positions and prints them as CSV which can be imported into excel and subsequently confluence
    def getPositions(self):

        # Print table headers
        print("Cell,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15")
        for cell in self.cellPrefix:
            try:
                positions = caget_array([f'{cell}-AL-SERVO-{enc:02d}:MOT.RBV' for enc in range(1,16)])
                positions = [round(p,2) for p in positions]
                print(f'{cell}, ', end='')
                for p in positions:
                    print(f'{p}, ', end='')
                print()

            except Exception as e:
                #print(f'{bcolors.WARNING}{str(e)}{bcolors.ENDC}')
                print(f'{cell}, ',end='')
                for i in range(0,15):
                    print("NAN, ",end='')
                print()


helper = girderPositionHelper()

if len(sys.argv) < 2:
    print("Missing args:")
    print("L = Trigger load on all cells (except DDBA)")
    print("l = Show readback status on all cells (except DDBA)")
    quit()

if sys.argv[1] == 'l':
    helper.getAllLoaded()

if sys.argv[1] == 'L':
    helper.triggerLoad()

if sys.argv[1] == 'p':
    helper.getPositions()