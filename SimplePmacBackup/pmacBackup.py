import getopt, sys, re, os, datetime, os.path
from pkg_resources import require
require('dls_pmaclib')

from dls_pmaclib.dls_pmcpreprocessor import *
from dls_pmaclib.dls_pmacremote import *


class simpleBackup(object):
    def __init__(self):
        self.host = ''
        self.port = 1
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
        
        print self.motorIVariableDescriptions[0]
        self.pti = None
        self.debug = False
        self.ivarRaw = ''
        self.iVariables = []
        self.setComms()
        self.ivarDump()
        self.makeAxisPMC()

    def setComms(self):
        self.host = sys.argv[1]
        self.port = sys.argv[2]
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
    
    def makeAxisPMC(self):
        with open('Axis.pmc','w') as f: 
            for axis in range(1,9):
                f.write("\r;-------Axis " + str(axis) + "------:\r")
                for index, val in enumerate(self.iVariables):
                    #print str(index)
                    if index >= axis*100 and index < (axis+1)*100:
                        f.write('{: <24}{: <1}'.format("I" + str(index) + "=" + val,";"+self.motorIVariableDescriptions[index-(axis*100)]+"\r"))
                    if axis < 5:
                        if index >= 7000+(axis*10) and index < 7000+((axis+1)*10):
                            f.write("I" + str(index) + "=" + val + "\r")
                    else:
                        if index >= 7100+((axis-4)*10) and index < 7100+((axis-3)*10):
                            f.write("I" + str(index) + "=" + val + "\r")
                

def main():
	simpleBackup()


if __name__ == "__main__":
	main()
