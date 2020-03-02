import getopt, sys, re, os, datetime, os.path
from pkg_resources import require
from subprocess import Popen, PIPE
require('dls_pmaclib')

from dls_pmaclib.dls_pmcpreprocessor import *
from dls_pmaclib.dls_pmacremote import *


class simpleBackup(object):
    def __init__(self,tserv,port):
        self.host = tserv
        self.port = port
        self.globalIVariableDescriptions = {0:'Serial card number', 1:'Serial card mode',
        2:'Control panel port activation', 3:'I/O handshake control',
        4:'Communications integrity mode', 5:'PLC program control',
        6:'Error reporting mode', 7:'Phase cycle extension',
        8:'Real-time interrupt period', 9:'Full/abbreviated listing control',
        10:'Servo interrupt time', 11:'Programmed move calculation time',
        12:'Lookahead spline time', 13:'Foreground in-position check enable',
        14:'Temporary buffer save enable', 15:'Degree/radian control for user trig functions',
        16:'Rotary buffer request on point', 17:'Rotary buffer request off point',
        18:'Fixed buffer full warning point', 19:'Clock source I-variable number',
        20:'Macro IC 0 base address', 21:'Macro IC 1 base address',
        22:'Macro IC 2 base address', 23:'Macro IC 3 base address',
        24:'Main DPRAM base address', 25:'Reserved', 26:'Reserved', 27:'Reserved',
        28:'Reserved', 29:'Reserved', 30:'Compensation table wrap enable',
        31:'Reserved', 32:'Reserved', 33:'Reserved', 34:'Reserved', 35:'Reserved',
        36:'Reserved', 37:'Additional wait states', 38:'Reserved',
        39:'UBUS accessory ID variable display control', 40:'Watchdog timer reset value',
        41:'I-variable lockout control', 42:'Spline/PVT time control mode',
        43:'Auxiliary serial port parser disable', 44:'PMAC ladder program enable',
        45:'Foreground binary rotary buffer transfer enable',
        46:'P&Q-variable storage location',
        47:'DPRAM motor data foreground reporting period',
        48:'DPRAM motor data foreground reporting enable',
        49:'DPRAM background data reporting enable', 50:'DPRAM background data reporting period',
        51:'Compensation table enable', 52:'CPU frequency control',
        53:'Auxiliary serial port baud rate control',
        54:'Serial port baud rate control',
        55:'DPRAM background variable buffers enable',
        56:'DPRAM ASCII communications interrupt enable',
        57:'DPRAM motor data background reporting enable',
        58:'DPRAM ASCII communications enable', 59:'Motor/CS group select',
        60:'Filtered velocity sample time', 61:'Filtered velocity shift',
        62:'Internal message carriage return control', 63:'Control-X echo enable',
        64:'Internal response tag enable', 65:'Reserved', 66:'Reserved', 67:'Reserved',
        68:'Coordinate system activation control', 69:'Reserved',
        70:'Macro IC 0 node auxiliary register enable', 71:'Macro IC 0 node protocol type control',
        72:'Macro IC 1 node auxiliary register enable', 73:'Macro IC 1 node protocol type control',
        74:'Macro IC 2 node auxiliary register enable', 75:'Macro IC 2 node protocol type control',
        76:'Macro IC 3 node auxiliary register enable', 77:'Macro IC 3 node protocol type control',
        78:'Macro type 1 master/slave communications timeout',
        79:'Macro type 1 master/master communications timeout',
        80:'Macro ring check period', 81:'Macro maximum ring error count',
        82:'Macro minimum sync packet count', 83:'Macro parallel ring enable mask',
        84:'Macro IC# for master communications', 85:'Macro ring order number',
        86:'Reserved', 87:'Reserved', 88:'Reserved', 89:'Reserved',
        90:'VME address modifier', 91:'VME address modifier don\'t care bits',
        92:'VME base address bits A31-A24',
        93:'VME mailbox base address bits A23-A16 ISA DPRAM base address bits A23-A16',
        94:'VME mailbox base address bits A15-A08 ISA DPRAM base address bits A15-A14 & control',
        95:'VME interrupt level', 96:'VME interrupt vector',
        97:'VME DPRAM base address bits A23-A20', 98:'VME DPRAM enable',
        99:'VME address width control'}
        self.motorIVariableDescriptions = {0:'Activation control', 1:'Commutation enable',
        2:'Command output address', 3:'Position loop feedback address',
        4:'Velocity loop feedback address', 5:'Master position address',
        6:'Position following enable and mode', 7:'Master (handwheel) scale factor',
        8:'Position scale factor', 9:'Velocity-loop scale factor',
        10:'Power-on servo position address', 11:'Fatal following error limit',
        12:'Warning following error limit', 13:'Positive software position limit',
        14:'Negative software position limit', 15:'Abort/limit deceleration rate',
        16:'Maximum program velocity', 17:'Maximum program acceleration',
        18:'Reserved', 19:'Maximum jog/home acceleration',
        20:'Jog/home acceleration time', 21:'Jog/home S-curve time',
        22:'Jog speed', 23:'Home speed and direction', 24:'Flag mode control',
        25:'Flag address', 26:'Home offset', 27:'Position rollover range',
        28:'In-position band', 29:'Output/first phase offset',
        30:'PID proportional gain', 31:'PID derivative gain',
        32:'PID velocity feedforward gain', 33:'PID integral gain',
        34:'PID integration mode', 35:'PID acceleration feedforward gain',
        36:'PID notch filter coefficient N1', 37:'PID notch filter coefficient N2',
        38:'PID notch filter coefficient D1', 39:'PID notch filter coefficient D2',
        40:'Net desired position filter gain', 41:'Desired position limit band',
        42:'Amplifier flag address', 43:'Overtravel-limit flag address',
        44:'Reserved', 45:'Reserved', 46:'Reserved', 47:'Reserved', 48:'Reserved',
        49:'Reserved', 50:'Reserved', 51:'Reserved', 52:'Reserved', 53:'Reserved',
        54:'Reserved', 55:'Commutation table address offset',
        56:'Commutation table delay compensation', 57:'Continuous current limit',
        58:'Integrated current limit', 59:'User-written servo/phase enable',
        60:'Servo cycle period extension period', 61:'Current-loop integral gain',
        62:'Current-loop forward-path proportional gain', 63:'Integration limit',
        64:'Deadband gain factor', 65:'Deadband size', 66:'PWM scale factor',
        67:'Position error limit', 68:'Friction feedforward',
        69:'Output command limit', 70:'Number of commutation cycles (N)',
        71:'Counts per N commutation cycles', 72:'Commuation phase angle',
        73:'Phase finding output value', 74:'Phase finding time',
        75:'Phase position offset', 76:'Current-loop back-path proportional gain',
        77:'Magnetization current', 78:'Slip gain', 79:'Second phase offset',
        80:'Power-up mode', 81:'Power-on phase position address',
        82:'Current-loop feedback address', 83:'Commutation position address',
        84:'Current-loop feedback mask word', 85:'Backlash take-up rate',
        86:'Backlash size', 87:'Backlash hysteresis', 88:'In-position number of scans',
        89:'Reserved', 90:'Rapid mode speed select', 91:'Power-on phase position format',
        92:'Jog move calculation time', 93:'Reserved', 94:'Reserved',
        95:'Power-on servo position format', 96:'Command output mode control',
        97:'Position capture & trigger mode', 98:'Third resolver gear ratio',
        99:'Second resolver gear ratio'}
        self.motorI7000VariableDescriptions = {0:'Encoder/timer decode control',
        1:'Position compare channel select', 2:'Encoder capture control',
        3:'Capture flag select control', 4:'Encoder gated index select',
        5:'Encoder index gate state', 6:'Output mode select',
        7:'Output invert control', 8:'Output PFM direction signal invert control',
        9:'Hardware 1/T control'}
        self.pti = None
        self.debug = False
        self.macroCounter = 0
        self.ivarRaw = ''
        self.iVariables = []
        self.mVarRaw = ''
        self.mVariables = []
        self.macroNodes = list()
        self.macroVarRaw = ''
        self.macroVariables = list()
        self.setComms()
        self.macroDump()
        self.ivarDump()
        self.mVarPositionsDump()
        self.makeAxisPMC()
        self.makeEctPMC()
        self.makeControlPMC()
        #self.makePosPMC()
        self.makeMacroPMC()

    def setComms(self):
        print "Connecting to %s using port %s" % (self.host, self.port)
        self.pti=PmacTelnetInterface(verbose=False)
        self.pti.setConnectionParams(self.host,self.port)
        msg = self.pti.connect()
        if msg != None:
            print msg
        else:
            print 'Connected to a PMAC via "%s" using port %s.' % (self.host, self.port)

    def sendCommand(self,text):
        (returnStr, status) = self.pti.sendCommand(text)
        #print "" + text + "\r"
        if self.debug:
            print '%s --> %s' % (repr(text), repr(returnStr))
        return (returnStr)
    
    def ivarDump(self):
        #for val in range(0,200):
            #self.ivarRaw= self.ivarRaw + (self.sendCommand('i%d'%(val)).replace('\x06',''))
        self.ivarRaw = self.sendCommand("i0,1000,1").replace('\x06','')
        self.ivarRaw = self.ivarRaw+ self.sendCommand("i1000,1000,1").replace('\x06','')
        self.ivarRaw = self.ivarRaw+ self.sendCommand("i2000,1000,1").replace('\x06','')
        self.ivarRaw = self.ivarRaw+ self.sendCommand("i3000,1000,1").replace('\x06','')
        self.ivarRaw = self.ivarRaw+ self.sendCommand("i4000,1000,1").replace('\x06','')
        self.ivarRaw = self.ivarRaw+ self.sendCommand("i5000,1000,1").replace('\x06','')
        self.ivarRaw = self.ivarRaw+ self.sendCommand("i6000,1000,1").replace('\x06','')
        self.ivarRaw = self.ivarRaw+ self.sendCommand("i7000,1000,1").replace('\x06','')
        self.ivarRaw = self.ivarRaw+ self.sendCommand("i8000,140,1").replace('\x06','')
        self.iVariables = self.ivarRaw.splitlines()
    
    def mVarPositionsDump(self):
        self.mVarRaw = self.sendCommand("m162,32,100").replace('\x06','')
        self.mVariables = self.mVarRaw.splitlines()

    def macroDump(self):
        for a in range(0,62):
            self.macroCounter = self.macroCounter +1
            if self.macroCounter != 4 and self.macroCounter != 3 :
                self.macroNodes.append(a)
            elif self.macroCounter == 4:
                self.macroCounter = 0
        for a in self.macroNodes:
            msDecode = "ms"+str(a)+",i910"
            msCapture = "ms"+str(a)+",i912"
            msFlag = "ms"+str(a)+",i913"
            msDirection = "ms"+str(a)+",i918"

            self.macroVariables.append(msDecode + "=" + str(self.macroVarRaw+self.sendCommand(msDecode).replace('\x06','')))
            self.macroVariables.append(msCapture + "=" + str(self.macroVarRaw+self.sendCommand(msCapture).replace('\x06','')))
            self.macroVariables.append(msFlag + "=" + str(self.macroVarRaw+self.sendCommand(msFlag).replace('\x06','')))
            self.macroVariables.append(msDirection + "=" + str(self.macroVarRaw+self.sendCommand(msDirection).replace('\x06','')))
            
    
    def makeAxisPMC(self):
        with open('Axis.pmc','w') as f: 
            f.write("; "+str(datetime.date.today())+"\r")
            for axis in range(1,33):
                f.write("\r;-------Axis " + str(axis) + "------:\r")
                for index, val in enumerate(self.iVariables):
                    #print str(index)
                    if index >= axis*100 and index < (axis+1)*100:
                        f.write('{: <24}{: <1}'.format("I" + str(index) + "=" + val,";"+self.motorIVariableDescriptions[index-(axis*100)]+"\r"))
                    if axis < 5:
                        if index >= 7000+(axis*10) and index < 7000+((axis+1)*10):
                            f.write('{: <24}{: <1}'.format("I" + str(index) + "=" + val,";"+self.motorI7000VariableDescriptions[index - (7000+(axis*10))]+"\r"))                
                    else:
                        if index >= 7100+((axis-4)*10) and index < 7100+((axis-3)*10):
                            f.write('{: <24}{: <1}'.format("I" + str(index) + "=" + val,";"+self.motorI7000VariableDescriptions[index - (7100+((axis-4)*10))]+"\r"))

    def makeEctPMC(self):
        with open('ECT.pmc','w') as f: 
            f.write("; "+str(datetime.date.today())+"\r")
            for index, val in enumerate(self.iVariables):
                if index in range(8000,8140):
                    f.write("I" + str(index) + "=" + val+"\r")

    def makeControlPMC(self):
        with open('Control.pmc','w') as f: 
            f.write("; "+str(datetime.date.today())+"\r")
            for index, val in enumerate(self.iVariables):
                if index in range(100):
                    f.write('{: <24}{: <1}'.format("I" + str(index) + "=" + val,";"+self.globalIVariableDescriptions[index]+"\r"))
                if index in range(7000,7999):
                    f.write("I" + str(index) + "=" + val+"\r")

    def makePosPMC(self):
        with open('POS.pmc','w') as f: 
            f.write("; "+str(datetime.date.today())+"\r")
            for index, val in enumerate(self.mVariables):
                if index in range(32):
                    f.write("M" + str(162+(index*100)) + "=" + val+"\r")

    def makeMacroPMC(self):
        valid = False
        with open('MACRO.pmc','w') as f: 
            f.write("; "+str(datetime.date.today())+"\r")
            for val in self.macroVariables:
                    if "ERR" not in val:
                        f.write(val)
                        valid = True
            if valid != True:
                os.system("rm MACRO.pmc")

def main():

    # Root dir for the motion area
    motionRoot = "/dls_sw/work/motion/"

    # Terminal server host name, assumes tserv 01
    tserv = sys.argv[1].lower()+"-nt-tserv-01"

    # Length of the geobrick prefix
    brickPrefixLength = sys.argv[1].__len__()+"-MO-STEP-".__len__()

    # Get all beamline folders
    stdout = Popen('ls '+motionRoot, shell=True, stdout=PIPE).stdout
    folders = stdout.read().split()

    # Check the beamline in the argument exists
    if sys.argv[1] not in folders:
        print "Beamline not found"
        quit()

    # Settings directory for the beamline specific motion area
    beamlineSettingDir = motionRoot+sys.argv[1]+"/Settings/"

    # Get a list of all the bricks
    stdout = Popen('ls '+beamlineSettingDir + "| grep "+sys.argv[1]+"-MO-STEP", shell=True, stdout=PIPE).stdout
    bricks = stdout.read().split()

    # Run the backup for each brick and move the files into the right area
    for brick in bricks:
        port = str("70"+brick[brickPrefixLength:])
        simpleBackup(tserv,port)
        os.system("mv *.pmc "+beamlineSettingDir+brick+"/Variables/")


if __name__ == "__main__":
	main()
