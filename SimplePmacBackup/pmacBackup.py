import getopt, sys, re, os, datetime, os.path
from pkg_resources import require
require('dls_pmaclib')

from dls_pmaclib.dls_pmcpreprocessor import *
from dls_pmaclib.dls_pmacremote import *


class simpleBackup(object):
    def __init__(self):
        self.host = ''
        self.port = 1
        self.pti = None
        self.debug = False
        self.setComms()
        self.sendCommand("i103")

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
        if self.debug:
            print '%s --> %s' % (repr(text), repr(returnStr))
        return (returnStr, status)


def main():
	simpleBackup()


if __name__ == "__main__":
	main()
