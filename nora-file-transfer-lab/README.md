# CS4375 - Race Condition File Transfer Lab
--
*by super anonymous student, last update October 16th, 2018*
## Overview
This is a *very* simple file transfer server/client setup. The server accepts client connections and puts all files within the same folder. The client can only send files that are in the same directory as the fileTransferClient.py file. The server is capable of handling multiple connections and transfers at once, using threads. If two clients attempt to upload a file of the same name, the server will overwrite the file with the client to last initiate transfer.

Note that server behavior has been modified to allow file overwriting in general -- that is, if you upload a file of the same name of another file, no error is raised as this is permitted behavior.

The server maintains different locks for each filename using a dictionary. After reading in the filename, the server gets the absolute filepath. The absolute filepath is used as the key in the dictionary. The server first checks if the filepath exists in the dictionary -- if not, it creates a new lock for that filepath and inserts it as an entry into the dictionary.

Before writing to the file, the server will attempt to acquire the lock associated with the file's absolute filepath in the dictionary. If it cannot, it blocks until it can. When it does, it creates or overwrites the file with the file transferred from the client. It does not release the lock until file transfer is complete.

The client first sends a framed message (using code provided by Dr. Freudenthal) indicating the file name to the server. The server then responds with either an error code or an acknowledgement to proceed with upload. The client then uploads the entire file using a modified version of the framedSend code that breaks the message into 100 byte chunks. The framedReceive code is used to handle receiving the file, that is then written to disk. The process completes with the server sending either an error or completion acknowledgement.

Much of the transfer/receive/thread code was provided by Dr. Freudenthal or sampled from the previous lab submission.

## Running Instructions
To run the lab, simply download or clone the repository and run the server script using `python3`. For example:

`python3 nora-file-transfer-lab/framedFileThreadServer.py` or `./file-transfer-lab/framedFileThreadServer.py`

Then, start any number of clients in a similar fashion:

`python3 file-transfer-lab/framedFileThreadClient.py` or `./file-transfer-lab/framedFileThreadClient.py`

You may also wish to use the stammer proxy provided. To do so, simply run the proxy and change the port that the client connects to, either by editing the script or using the server flag.

## References
Much of the code for sending and receiving messages was provided by Dr. Freudenthal.

The Python documentation describing sockets was consulted, though I'm not sure if I used much of it. (https://docs.python.org/2/library/socket.html)

I also had to look up how to define Enums in Python, since I wanted to use those for server states.

I also referenced this StackOverflow question that covered reading and writing a file by its bytes rather than lines (https://stackoverflow.com/questions/6787233/python-how-to-read-bytes-from-file-and-save-it).

I also read over this document on thead synchronization/locks: http://effbot.org/zone/thread-synchronization.htm#locks.

Additionally, I looked up how to get an absolute file path for a file: https://stackoverflow.com/questions/51520/how-to-get-an-absolute-file-path-in-python.

Lastly, I referred to the threading documentation in Python's docs for Lock and RLock: https://docs.python.org/3/library/threading.html.