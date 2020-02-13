# This script simulates the laserPuckPointer hardware to allow testing of the support module and
# streamDevice. Run this on a local machine and point the AsynIP port to localhost:8000.

import socket
from threading import *
import re
import array as arr

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = "localhost"
port = 6789
print (host)
print (port)
serversocket.bind((host, port))
flag = 1

class client(Thread):
    def __init__(self, socket, address):
        Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.lastCommand = ""
        self.command = ""
        self.start()
        self.positions=[12,22]
        self.demandPos=[0,0]
        self.movingFlag=[0,0]
        self.velo=[1,1]
        self.axis = 0


    def run(self):
        while 1:
            buffer = self.sock.recv(1024)
            self.lastCommand+=buffer.decode('ascii')
            if self.lastCommand == "":
                self.sock.close()
                break
            # Check if we get a LF to signify end of command

            if '\r' in self.lastCommand:
                self.command = self.lastCommand.split('\r')[0]
                self.lastCommand = self.lastCommand.split('\r',1)[-1]

                for a in self.command:
                    print(hex(ord(a)) + " ")

                #for a in self.lastCommand:
                    #print(hex(ord(a)) + " ")

                print("\n")
                print(f'Pos 1 = {self.positions[0]}, Pos 2 = {self.positions[1]}')
                #If it's a read
                if '#1' in self.command:
                    #addressing axis 1
                    axis = 1
                elif '#2' in self.command:
                    #addressing axis 1
                    axis = 2
                if 'p' in self.command:
                    #Asking position
                    #print("Axis = "+str(axis) + "\n")
                    self.sock.send((str(self.positions[axis-1])+"\r\n").encode())
                if 'j=' in self.command:
                    #Do a jog command
                    print("Really got a jog command this time\n")
                    demand = int(float(self.command.split('=')[1]))
                    print(f'Got a j={demand} command')
                    self.positions[axis-1]=demand
                if 'j^' in self.command:
                    #Do a jog command
                    self.positions[axis-1]+=self.command.split('^')[1]


serversocket.listen(1)
print ('server started and listening')
while flag==1:
    clientsocket, address = serversocket.accept()
    client(clientsocket, address)