# python 3

from socket import *
import thread
import sys
import time
import random

portadd = 12000
bufsize = 1024
localhost = '127.0.0.1'

class peer_node:

    def __init__(self,id,sucsr1,sucsr2,interval):
        self.id = id
        self.port = 12000 + id
        self.sucsr1 = sucsr1
        self.sucsr2 = sucsr2
        self.predr1 = 0
        self.predr2 = 0
        self.interval = interval
        self.udpsocket = socket(AF_INET, SOCK_DGRAM)
        self.udpserss = socket(AF_INET, SOCK_DGRAM)

    # while 1 : loop -> time.sleep(choose a time) to let it run endless
    def udp_ping(self):
        ADDR1 = (localhost, self.sucsr1+portadd)
        ADDR2 = (localhost, self.sucsr2+portadd)
        while 1:
            self.udpsocket.sendto('s1'.encode(), ADDR1)
            self.udpsocket.sendto('s2'.encode(), ADDR2)
            print('Ping requests sent to Peers %d and %d' % (self.sucsr1+portadd, self.sucsr2+portadd))        #later
            self.udpsocket.settimeout(1.0)              # what value will be better?
            try:
                data,addr = self.udpsocket.recvfrom(bufsize)
            except:
                pass
            else:
                if addr[1] == self.sucsr1+portadd:
                    print('Ping response received from peer %d' % self.sucsr1+portadd)
                elif addr[1] == self.sucsr2+portadd:
                    print('Ping response received from peer %d' % self.sucsr2+portadd)
            time.sleep(10)
            # change this value later

    def udp_server(self):
        address = (localhost,self.port)
        self.udpserss.bind(address)
        while 1:
            data, addr = self.udpserss.recvfrom(bufsize)
            self.udpserss.sendto('rsp'.encode(), addr)
            if data[1] == 'scsor1':
                self.udpserss.sendto('rsp1'.encode(), addr)
                self.predr1 = addr[1] - portadd
                #update predecessors
            else:
                self.udpserss.sendto('rsp2'.encode(), addr)
                self.predr2 = addr[2] - portadd
            print('Ping request received from peer %d' % addr[1] - portadd)
            # add command here

        self.udpserss.close()

    def tcp_listen(self,port):
        # establish a socket to endless listen
        serverSocket = socket(AF_INET, SOCK_STREAM)
        address = (localhost, port)
        serverSocket.bind(address)
        serverSocket.listen(6)
        while 1:
            connectSocket, addr = serverSocket.accept()
            # actually, is hould start a new thread here to deal with the new connect
            # cmnct_socket recv client socket, and addr recv ip address and port respectively
            # the initial socket is used to wait for communication while the second is used to communicate.
            data = connectSocket.recv(bufsize)
            self.tcp_server(connectSocket, addr, data)
            connectSocket.close()

    def tcp_server(self,connectSocket,addr,data):

        inf = data.split()
        try:
            req = inf[0]
        except:
            return
            # if some one left by both way, update the p2p circle
            # so, where to put these update? in class or glocal value?
        if req == 'join':   # 'join number'
            if (self.id < inf[1] and inf[1] < self.sucsr1) or (self.id > inf[1] and self.sucsr1 > inf[1]):
                msg = 'jhere %d %d %s' %(self.sucsr1,self.sucsr2,inf[1])
                connectSocket.sendto(msg.encode(),addr)
                self.sucsr1 = addr[1] - portadd
                self.sucsr2 = self.sucsr1
                print('Peer %s Join request received' %inf[1])   # or 'Join request has been accepted'
                print('My new first successor is Peer %s' % self.sucsr1)
                print('My new second successor is Peer %s' % self.sucsr2)
                # peer joins here, and update its own sucsr
            elif self.id == inf[1]:
                # return self.id???
                pass
            elif self.id > inf[1]:
                msg = self.tcp_client(data,self.sucsr1-portadd)
                req = msg.split()
                print('Peer %s Join request forwarded to my successor' % inf[1])
                # then back the msg to pre
                if req[0] == 'jhere':  # 'jhere s1 s2'
                    print('Successor Change request received')
                    self.sucsr2 = msg[3]
                    print('My new first successor is Peer %s' % self.sucsr1)
                    print('My new second successor is Peer %s' % self.sucsr2)
                    msg = 'there %s %s' % (msg[1], msg[2])
                    connectSocket.sendto(msg.encode(), addr)
                    # send back to its predsr
                else:
                    connectSocket.sendto(msg, addr)     # can i send array??

        elif req == 'blabla':
            pass
        elif req == 'blabla':
            pass
        connectSocket.close()

    def tcp_client(self,port,msg=None):
        clientSocket = socket(AF_INET, SOCK_STREAM)
        addr = (localhost,port)
        clientSocket.connect(addr)
        clientSocket.send(msg.encode())
        data = clientSocket.recv(bufsize)
        clientSocket.close()
        return data

class join_dht:
    peerSocket = socket(AF_INET, SOCK_STREAM)


    def __init__(self,peer,kpeer):
        self.id = peer
        self.s1 = -1
        self.s2 = -1
        #self.port = peer + portadd
        self.peerport = kpeer + portadd

    def tcp_join(self):
        # ADDR = (localhost, self.id + portadd)
        # self.peerSocket.bind(ADDR)
        addr = (localhost, self.peerport)
        self.peerSocket.connect(addr)
        command = 'join %d' %self.id
        self.peerSocket.send(command.encode())
        data = self.peerSocket.recv(bufsize)
        try:
            data    # 'there s1 s2'
        except:
            pass
        else:
            self.s1 = data[1]
            self.s2 = data[2]
        self.peerSocket.close()

'''
class input(sth):
    if sth == 'Store':
        pass
    if sth == 'Quit':
        pass
    #blablabla

def hashfunction(filename):
    value = int(filename%256)
    return value

# 2->7->12->18->2
def storeFile(filename,id,prede,suc):
    value = hashfunction(filename)
    if id < value & id < suc:     # in case 19
        print('File Store %d request forward to my successor' %filename)
        pass
        # use tcp to push this value to its 1st successor
    if id >= value & value > prede:  # in case insert at 12 and value is 4
        #store in this node. but there is an issue: how to push 2 form 18? i need prede?
        print(' File Store %d request accepted' %filename)
        pass
'''

def main():
    print('test')

if __name__ == '__main__':
    main()

