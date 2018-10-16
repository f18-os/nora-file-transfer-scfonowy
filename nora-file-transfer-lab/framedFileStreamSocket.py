from framedSock import FramedStreamSock
import re, os
from enum import Enum

# enum for what state we're in when receiving a file
class FileReceiveState(Enum):
    NAME = 1
    FILE = 2
    COMPLETE = 3
    ERROR = 4

# enum for what state we're in when receiving a message
class MessageReceiveState(Enum):
    LENGTH = 1
    PAYLOAD = 2
    COMPLETE = 3
    ERROR = 4

class FramedFileStreamSock(FramedStreamSock):
    ### BEGIN CODE CITED FROM PROVIDED CODE
    def receivemsg(self):
        state = MessageReceiveState.LENGTH
        payload = None
        msgLength = -1

        while state != MessageReceiveState.COMPLETE and state != MessageReceiveState.ERROR: # check for terminal states
            r = self.sock.recv(100) # read part of message and update buffer
            self.rbuf += r

            if (state == MessageReceiveState.LENGTH): # parse length
                match = re.match(b'([^:]+):(.*)', self.rbuf, re.DOTALL | re.MULTILINE) # look for colon
                if match:
                    lengthStr, self.rbuf = match.groups()

                    try: 
                        msgLength = int(lengthStr)
                        state = MessageReceiveState.PAYLOAD
                    except:
                        state = MessageReceiveState.ERROR
                        if len(self.rbuf):
                            print("badly formed message length:", lengthStr)
            

            if state == MessageReceiveState.PAYLOAD: # check if payload is complete
                if len(self.rbuf) >= msgLength: # truncate message
                    payload = self.rbuf[0:msgLength]
                    self.rbuf = self.rbuf[msgLength:]
                    state = MessageReceiveState.COMPLETE

            # error/zero length case
            if not r or len(r) == 0:
                state = MessageReceiveState.ERROR
                if len(self.rbuf) != 0:
                    print("FramedReceive: incomplete message. \n  state=%s, length=%d, rbuf=%s" % (state, msgLength, self.rbuf))
                payload = None # don't return partial message

            if self.debug:
                print("FramedReceive: state=%s, length=%d, rbuf=%s" % (state, msgLength, self.rbuf))

        return payload
    ### END CODE CITED FROM PROVIDED CODE

### BEGIN CODE CITED FROM PREVIOUS ASSIGNMENT
    # function that sends a file 100 bytes at a time. sampled from framedSend
    def send_file(self, filename):
        # check if file exists
        if not os.path.isfile(filename):
            print("FileSend: file does not exist.")
            return

        # send the name of the file, since we know it exists now
        self.sendmsg(filename.encode())

        # get name acknowledgement and check if we can proceed with send
        if FileReceiveState(int(self.receivemsg().decode())) == FileReceiveState.ERROR:
            print("FileSend: unable to send file, file may exist.")
            return

        # open file and get file length
        sendingFile = open(filename, "rb")
        fileLength = os.path.getsize(filename)
        if self.debug: print("file size: " + str(fileLength))
        
        fileBytes = sendingFile.read(100) # construct header w/ initial portion of message
        headerMsg = (str(fileLength) + ":").encode() + fileBytes
        if self.debug: print("sending header: " + str(headerMsg))

        # send first part of message (length + first chunk)
        self.sock.send(headerMsg)

        # send rest of the file 100 bytes at a time
        fileBytes = sendingFile.read(100)
        while len(fileBytes) > 0:
            if self.debug: print("sending next 100 bytes...")
            self.sock.send(fileBytes)
            fileBytes = sendingFile.read(100)

        # check status
        if FileReceiveState(int(self.receivemsg().decode())) == FileReceiveState.ERROR:
            print("FileSend: error sending file, try again.")

        
    # function that receives a file over the network. makes use of framedReceive.
    def receive_file(self, directory):
        # NOTE: this is kind of overengineered. there's no need for a loop here, but i thought
        # the problem would be more involved than it was, and was too lazy to refactor it. :(
        state = FileReceiveState.NAME # set first state of 
        filename = None

        while state != FileReceiveState.COMPLETE and state != FileReceiveState.ERROR:
            if state == FileReceiveState.NAME: # get filename using framedReceive
                filename = self.receivemsg()
                if filename == None:
                    state = FileReceiveState.ERROR
                    print("FileReceive: unable to read filename. \n")
                elif os.path.isfile(directory + str(filename.decode())):
                    state = FileReceiveState.ERROR
                    print("FileReceive: file already exists. \n")
                else:
                    filename = str(filename.decode())
                    state = FileReceiveState.FILE
                    if self.debug: print("FileReceive: ready to receive file %s" % (filename))
            
            elif state == FileReceiveState.FILE: # get file using framedReceive
                fileBytes = self.receivemsg()
                if fileBytes == None:
                    state = FileReceiveState.ERROR
                    print("FileReceive: error receiving file. \n")
                else:
                    try: # write file to system
                        outputFile = open(directory + filename, "wb")
                        outputFile.write(fileBytes)
                        outputFile.close()
                        state = FileReceiveState.COMPLETE
                    except Exception as e:
                        state = FileReceiveState.ERROR
                        print("FileReceive: error writing file: " + str(e))

            self.sendmsg(str(state.value).encode()) # indicate error/ready to continue
### END CODE CITED FROM PREVIOUS ASSIGNMENT