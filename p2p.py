# python 3

from socket import *
import threading
import sys
import time

PORTADD = 12000
BUFSIZE = 1024
INITNUM = 0
localhost = '127.0.0.1'

class peer_node:
    def __init__(self, id, sucsr1, sucsr2, interval):
        self.id = id
        self.sucsr1 = sucsr1
        self.sucsr2 = sucsr2
        self.predr1 = INITNUM
        self.predr2 = INITNUM
        self.communicate = transmission(interval, id, sucsr1, sucsr2)

    def send_ping(self):
        # do i need two independent threads to deal with this? nope, upd just needs one socket
        ADDR1 = (localhost, self.sucsr1 + PORTADD)
        ADDR2 = (localhost, self.sucsr2 + PORTADD)
        msg1 =
        cnt = INITNUM
        while 1:
            self.communicate.udp_ping()
            print('Ping requests sent to Peers %d and %d' % (self.sucsr1 + PORTADD, self.sucsr2 + PORTADD))



class transmission:
    def __init__(self, interval, id, sucsr1, sucsr2):
        self.udpsocket = socket(AF_INET, SOCK_DGRAM)
        self.udpserss = socket(AF_INET, SOCK_DGRAM)
        self.interval = interval
        self.port = PORTADD + id

    def udp_ping(self, msg, addr):
        self.udpsocket.sendto(msg.encode(), addr)

        self.udpsocket.settimeout(1.0)
        try:
            data, addr = self.udpsocket.recvfrom(BUFSIZE)
        except:
            # here is the sucs dead
            if cnt >= 3:
                cnt += 1
                pass
            msg = 'depar s1'
            self.departure(msg)
            continue
        else:
            if addr[1] == int(self.sucsr1 + PORTADD):
                print('Ping response received from peer %d' % self.sucsr1 + PORTADD)
            elif addr[1] == int(self.sucsr2 + PORTADD):
                print('Ping response received from peer %d' % self.sucsr2 + PORTADD)
        time.sleep(10)
        # may change this value later; this set the time that send to next ping

    def udp_server(self):
        address = (localhost, self.port)
        self.udpserss.bind(address)
        while 1:
            data, addr = self.udpserss.recvfrom(BUFSIZE)
            data = data.split()
            #self.udpserss.sendto('rsp'.encode(), addr)
            if data[1] == 'scsor1':
                self.udpserss.sendto('rsp1'.encode(), addr)
                self.predr1 = addr[1] - PORTADD
                #update predecessors
            else:
                self.udpserss.sendto('rsp2'.encode(), addr)
                self.predr2 = addr[2] - PORTADD
            print('Ping request received from peer %d' % addr[1] - PORTADD)
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
            data = connectSocket.recv(BUFSIZE)
            th = threading.Thread(target=self.tcp_server,args=(connectSocket, addr, data))
            th.start()

    def tcp_server(self,connectSocket,addr,data):

        inf = data.split()
        try:
            req = inf[0]
        except:
            return
            # if some one left by both way, update the p2p circle
            # so, where to put these update? in class or glocal value?
        if req == 'join':   # 'join number'
            if  (self.id < inf[1] and inf[1] < self.sucsr1) or \
                (self.id < inf[1] and self.id > self.sucsr1) or \
                (self.id > inf[1] and self.sucsr1 > inf[1] and self.id > self.sucsr1):
                # e.g. 24-> 28(in)-> 32 || 56-> 59(in) ->4 || 56-> 2(in) ->4
                msg = 'jhere %d %d %s' %(self.sucsr1,self.sucsr2,inf[1])
                connectSocket.sendto(msg.encode(),addr)
                self.sucsr1 = addr[1] - PORTADD
                self.sucsr2 = self.sucsr1
                print('Peer %s Join request received' %inf[1])   # or 'Join request has been accepted'
                print('My new first successor is Peer %s' % self.sucsr1)
                print('My new second successor is Peer %s' % self.sucsr2)
                # peer joins here, and update its own sucsr
            elif self.id == inf[1]:
                # return self.id???
                pass
            elif self.id > inf[1]:
                msg = self.tcp_client(data, self.sucsr1 - PORTADD)
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

        elif req == 'store':    # store value filename
            if  (self.id <= inf[1] and inf[1] < self.sucsr1) or \
                (self.id <= inf[1] and self.id > self.sucsr1) or \
                (self.id > inf[1] and self.sucsr1 > inf[1] and self.id > self.sucsr1):
                print('Store %s request accepted' % inf[2])

            elif self.id > inf[1]:
                print(' Store %s request forwarded to my successor' % inf[2])

        elif req == 'request':
            if  (self.id <= inf[1] and inf[1] < self.sucsr1) or \
                (self.id <= inf[1] and self.id > self.sucsr1) or \
                (self.id > inf[1] and self.sucsr1 > inf[1] and self.id > self.sucsr1):
                print('File request for %s has been sent to my successor' % inf[2])
                #how to send file???
            elif self.id > inf[1]:
                print(' Request for File %s has been received, but the file is not stored here' % inf[2])

        elif req == 'quit':
            # all data store in inf array
            # quit selfid suc1 suc2
            # if quit, then it will sends tcp to pres, therefore itneeds to sends it succ
            if inf[1] == self.sucsr1:
                self.sucsr1 = inf[2]
                self.sucsr2 = inf[3]
                print('Peer %s will depart from the network' %inf[1])
                print('My new first successor is Peer %s' %inf[2])
                print('My new second successor is Peer %s' % inf[3])
            elif inf[1] == self.sucsr2:
                self.sucsr2 = inf[2]
                print('Peer %s will depart from the network' % inf[1])
                print('My new second successor is Peer %s' % inf[2])

        elif req == 'depar':
            # departure, ask for sucs
            # depar its_id
            # by udp func, this node's pre will update at that place
            msg = '%d %d' % (self.sucsr1, self.sucsr2)
            connectSocket.sendto(msg.encode(), addr)
        connectSocket.close()

    def departure(self,msg):
        if msg == 'depar s1':
            # its sucs1 departure
            data = self.tcp_client().split()
            self.sucsr1 = self.sucsr2
            self.sucsr2 = int(data[0])
        elif msg == 'depar s2':
            data = self.tcp_client().split()
            if self.sucsr2 == int(data[0]):
                self.sucsr2 = int(data[1])
            else:
                # the sucs1 has already update
                self.sucsr2 = int(data[0])
        print('My new first successor is Peer %s' % self.sucsr1)
        print('My new second successor is Peer %s' % self.sucsr2)
        # data will be suc1 or suc2

    def tcp_client(self,port,msg=None):
        # port is the destination
        clientSocket = socket(AF_INET, SOCK_STREAM)
        addr = (localhost,port)
        clientSocket.connect(addr)
        clientSocket.send(msg.encode())
        data = clientSocket.recv(BUFSIZE)
        clientSocket.close()
        return data

class join_dht:
    peerSocket = socket(AF_INET, SOCK_STREAM)

    def __init__(self,peer,kpeer):
        self.id = peer
        self.s1 = -1
        self.s2 = -1
        #self.port = peer + portadd
        self.peerport = kpeer + PORTADD

    def tcp_join(self):
        # ADDR = (localhost, self.id + portadd)
        # self.peerSocket.bind(ADDR)
        addr = (localhost, self.peerport)
        self.peerSocket.connect(addr)
        command = 'join %d' %self.id
        self.peerSocket.send(command.encode())
        data = self.peerSocket.recv(BUFSIZE)
        try:
            data    # 'there s1 s2'
        except:
            pass
        else:
            self.s1 = data[1]
            self.s2 = data[2]
        self.peerSocket.close()

def input_command(node):
    while 1:
        command = input().lower().split()
        if len(command) == 2 and command[0] == 'store':
            #print('Store %s' %command[1])
            filename = int(command[1])
            msg = 'store %d %d' % (hashfunction(filename), filename)
            node.tcp_cline(node.sucsr1 + PORTADD, msg)
            print('Store %d request forwarded to my successor' % filename)

        elif len(command) == 2 and command[0] == 'request':
            filename = int(command[1])
            msg = 'request %d %d' % (hashfunction(filename), filename)
            node.tcp_cline(node.sucsr1 + PORTADD, msg)
            print('File request for %d has been sent to my successor' % filename)

        elif len(command) == 1 and command[0] == 'quit':
            msg = 'quit %d %d %d' % (node.id, node.sucsr1, node.sucsr2)
            node.tcp_client(node.predr1 + PORTADD, msg)
            node.tcp_client(node.predr2 + PORTADD, msg)
            sys.exit()
        else:
            print('Command invalid')

def hashfunction(filename):
    value = int(filename%256)
    return value

def main():
    if sys.argv[1] == 'init':
        if len(sys.argv) != 6:
            print('Wrong arguments')
            sys.exit()
        node = peer_node(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
        t1 = threading.Thread(target=input_command, args=(node,))
        # why i have to put a comma here?

        t1.start()

if __name__ == '__main__':
    main()

