import logging
from threading import *
import socket

class Connection(Thread):
    def __init__(self, ipAddress, portNumber):
        Thread.__init__(self)
        self.ipAddress = ipAddress
        self.portNumber = portNumber
        self.buffer = ""
        self.start()

class TCPServer(Connection):
    def __init__(self,ipAddress,portNumber):
        Connection.__init__(self,ipAddress,portNumber)


    def run(self):

        # Configure the socket
        tcpCommandServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Allow the socket to be re-used even if it's in TIME_WAIT state
        try:
            tcpCommandServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,tcpCommandServer.getsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR) | 1)
        except socket.error:
            pass


        tcpCommandServer.bind((self.ipAddress, self.portNumber))
        tcpCommandServer.listen()
        print(f"Listening on {self.ipAddress}:{self.portNumber} (TCPCommandServer)")

        self.serverSocket, address = tcpCommandServer.accept()
        print("Client connected on TCPCommandServer")

        while True:
            self.buffer+=self.serverSocket.recv(4096).decode()
            print(bytes(self.buffer,"utf-8"))



port = 8000
TCPServer("localhost",port)
