#! /usr/bin/env python3
import sys, os, socket, params, time
from threading import Thread, RLock
from framedFileStreamSocket import FramedFileStreamSock

### BEGIN PROVIDED CODE
switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)
class ServerThread(Thread):
    receiptDirectory = "./received_files/" # directory used to store files
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedFileStreamSock(sock, debug), debug
        self.start()
### END PROVIDED CODE

    def run(self):
        while True:
            try:
                if self.debug: print("awaiting file")
                self.fsock.receive_file(ServerThread.receiptDirectory)
            except Exception as e: # most likely, client disconnected
                print("connection closed: " + str(e))
                quit()


while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
