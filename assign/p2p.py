# python 3

# file pass to better node
# a peer dies before it forwards a message
# can't divide the function of udp server


from socket import *
import threading
import sys
import time

PORTADD = 12000
BUFSIZE = 1024
INITNUM = 0
MAXLOST = 3
MAXSOCKET = 6
LOCALHOST = '127.0.0.1'

class peer_node:
    def __init__(self, id, sucsr1, sucsr2, interval):
        self.id = id
        self.sucsr1 = sucsr1
        self.sucsr2 = sucsr2
        self.predr1 = INITNUM
        self.predr2 = INITNUM
        self.interval = interval
        self.communicate = transmission(id)

    # send ping ti its successors
    def send_ping(self):
        # do i need two independent threads to deal with this? nope, upd just needs one socket
        cnt1 = INITNUM
        cnt2 = INITNUM
        while 1:
            ADDR1 = (LOCALHOST, self.sucsr1 + PORTADD)
            ADDR2 = (LOCALHOST, self.sucsr2 + PORTADD)
            cnt1, data1, addr1 = self.communicate.udp_ping('scsor1 %s' % self.id, ADDR1, cnt1)
            cnt2, data2, addr2 = self.communicate.udp_ping('scsor2 %s' % self.id, ADDR2, cnt2)
            # the udp server needs to know which successor it is, then it can update its predecessors
            print('Ping requests sent to Peers %s and %s' % (self.sucsr1, self.sucsr2))
            if cnt1 >= MAXLOST:
                print('Peer %d is no longer alive' %self.sucsr1)
                msg = 'depar s1'
                self.departure(msg)
            elif data1 != 'norecv':
                print('Ping response received from peer %s' % self.sucsr1)
            if cnt2 >= MAXLOST:
                print('Peer %d is no longer alive' % self.sucsr2)
                msg = 'depar s2'
                self.departure(msg)
            elif data2 != 'norecv':
                print('Ping response received from peer %s' % self.sucsr2)
            time.sleep(self.interval)
            # sleep for 10 seconds then ping again

    # recv ping from its predsors
    def recv_ping(self):
        self.communicate.udp_server(self)

    # deal with received udp information
    def udp_inf(self, data, addr):
        # how can i extract this part of function to class peer_node ?
        if data[0].decode() == 'scsor1':
            # this information come from its first (nearest) predecessor
            self.predr1 = int(data[1])
            # update its predecessors
        else:
            self.predr2 = int(data[1])

    # start to listen tcp
    def tcp_lisn(self):
        self.communicate.tcp_listen(self.communicate.port, self)

    # deal with tcp info. recved
    def tcp_server(self, connectSocket, addr, data):
        inf = data.decode().split()
        try:
            req = inf[0]
        except:
            print('Something went wrong')
            connectSocket.close()
            return
        # PEER WANT TO JOIN
        if req == 'join':   # data = 'join number'
            inf[1] = int(inf[1])
            if  (self.id < inf[1] and inf[1] < self.sucsr1) or \
                (self.id < inf[1] and self.id > self.sucsr1) or \
                (self.id > inf[1] and self.sucsr1 > inf[1] and self.id > self.sucsr1):
                # e.g. 24-> 28(in)-> 32 || 56-> 59(in) ->4 || 56-> 2(in) ->4
                msg = 'jhere %s %s %s' %(self.sucsr1, self.sucsr2, inf[1])
                # its sucsors will become the joined peers' sucsors
                connectSocket.send(msg.encode())
                # send back
                self.sucsr2 = self.sucsr1
                self.sucsr1 = int(inf[1])
                print('Peer %s Join request received' % inf[1])   # or 'Join request has been accepted'
                print('My new first successor is Peer %s' % self.sucsr1)
                print('My new second successor is Peer %s' % self.sucsr2)
                # peer joins here, and update its own successor
            elif self.id > inf[1]:
                msg = self.communicate.tcp_client(self.sucsr1 + PORTADD, data)
                # send forward and wait for return msg
                print('Peer %s Join request forwarded to my successor' % inf[1])
                try :
                    req = msg.decode().split()
                    req[0]
                except:
                    print('join information is not correct')
                else:
                    if req[0] == 'jhere':  # 'jhere s1 s2 joinpeerid'
                        print('Successor Change request received')
                        self.sucsr2 = int(req[3])
                        print('My new first successor is Peer %s' % self.sucsr1)
                        print('My new second successor is Peer %s' % self.sucsr2)
                        msg = 'there %s %s' % (req[1], req[2])
                        connectSocket.send(msg.encode())
                        # send back to its predecessor
                    # else just like a router passing the information without change
                    else:
                        connectSocket.send(msg)     # can i send array??
            # elif self.id == inf[1]:
            #    print('The peer has already exist')
            # no need to consider this scenario
        # STORE A FILE
        elif req == 'store':    # store value filename
            inf[1] = int(inf[1])
            if  (self.id >= inf[1] and inf[1] > self.predr1) or \
                (self.id >= inf[1] and self.id < self.predr1) or \
                (self.id < inf[1] and self.id < self.predr1 and self.predr1 < inf[1]):
                print('Store %s request accepted' % inf[2])
                f = open(inf[2]+'.pdf','w')
                f.write('Hello! This is file %s' % inf[2])
                f.close()

            elif self.id < inf[1]:
                print(' Store %s request forwarded to my successor' % inf[2])
                self.communicate.tcp_client(self.sucsr1+PORTADD, data)
        # REQUEST A FILE
        elif req == 'request':  # store value filename client_id
            inf[1] = int(inf[1])
            if  (self.id >= inf[1] and inf[1] > self.predr1) or \
                (self.id >= inf[1] and self.id < self.predr1) or \
                (self.id < inf[1] and self.id < self.predr1 and self.predr1 < inf[1]):
                print('File %s is stored here' % inf[2])
                # connect to peer directly
                ftfSocket = socket(AF_INET, SOCK_STREAM)
                port = int(inf[3]) + PORTADD
                adr = (LOCALHOST, port)
                ftfSocket.connect(adr)
                ftfSocket.send(('sending %s %s' % (inf[2], self.id)).encode())
                f = open(inf[2] + '.pdf', 'rb')
                print('Sending file %s to Peer %s' % (inf[2], inf[3]))
                while 1:    # using this loop to read the whole file
                    line = f.read(BUFSIZE)
                    if not line:
                        print('The file has been sent')
                        break
                    while line:     # using this loop to send the whole BUFSIZE
                        ftfSocket.send(line)
                        line = f.read(BUFSIZE)
                f.close()
            elif self.id < inf[1]:
                print(' Request for File %s has been received, but the file is not stored here' % inf[2])
                self.communicate.tcp_client(self.sucsr1+PORTADD, data)
        # SEND A FILE
        elif req == 'sending':
            # receive a file: sending filename peerid
            print('Receiving File %s from Peer %s' %(inf[1], inf[2]))
            name = 'received_%s.pdf' % inf[1]
            f = open(name, 'wb')
            while 1:
                line = connectSocket.recv(BUFSIZE)
                if not line:
                    f.close()
                    print(' File %s received' % inf[1])
                    break
                while line:
                    f.write(line)
                    line = connectSocket.recv(BUFSIZE)
        # LEAVE (GRACEFUL)
        elif req == 'quit':
            # all data store in inf array
            # quit selfid suc1 suc2
            # if quit, then it will sends tcp to pres, therefore it needs to sends it sucor
            inf[1] = int(inf[1])
            if inf[1] == self.sucsr1:
                self.sucsr1 = int(inf[2])
                self.sucsr2 = int(inf[3])
                print('Peer %s will depart from the network' %inf[1])
                print('My new first successor is Peer %s' % self.sucsr1)
                print('My new second successor is Peer %s' % self.sucsr2)
            elif inf[1] == self.sucsr2:
                self.sucsr2 = int(inf[2])
                print('Peer %s will depart from the network' % inf[1])
                print('My new first successor is Peer %s' % self.sucsr1)
                print('My new second successor is Peer %s' % self.sucsr2)
        # SEND ALL SUCCESSORS' ID TO CLIENT
        elif req == 'depar':
            # inf = depar what_scsor_client_is
            # at udp func, this node's pre will update at that place
            msg = '%s %s' % (self.sucsr1, self.sucsr2)
            connectSocket.sendto(msg.encode(), addr)
        # CLOSE THIS FUNCTION
        connectSocket.close()

    # if the node's sucsor abrupt, called by udp_ping
    def departure(self, msg):
        # its sucs1 departure, ask sucor2 for inf.
        if msg == 'depar s1':
            data = self.communicate.tcp_client(self.sucsr2+PORTADD, msg).split()
            self.sucsr1 = self.sucsr2
            self.sucsr2 = int(data[0])

        # sucsor2 leave, ask scsor1 for inf.
        elif msg == 'depar s2':
            data = self.communicate.tcp_client(self.sucsr1+PORTADD, msg).split()
            if self.sucsr2 == int(data[0]):
                self.sucsr2 = int(data[1])
            else:
                # the sucs1 has already update
                self.sucsr2 = int(data[0])
        print('My new first successor is Peer %s' % self.sucsr1)
        print('My new second successor is Peer %s' % self.sucsr2)
        # data will be suc1 or suc2

class transmission:
    def __init__(self, id):
        self.udpsocket = socket(AF_INET, SOCK_DGRAM)
        self.udpserss = socket(AF_INET, SOCK_DGRAM)
        self.port = PORTADD + id

    def udp_ping(self, msg, addr, cnt=0):
        self.udpsocket.sendto(msg.encode(), addr)
        self.udpsocket.settimeout(1.0)
        try:
            data, addr = self.udpsocket.recvfrom(BUFSIZE)
        except:     # if no udp received
            cnt += 1
            data = 'norecv'
            return cnt, data, addr
        else:
            cnt = INITNUM
            return cnt, data, addr

    def udp_server(self, sct):
        address = (LOCALHOST, self.port)
        self.udpserss.bind(address)
        while 1:
            data, addr = self.udpserss.recvfrom(BUFSIZE)
            data = data.split()
            try:
                data[0]
            except:
                print('Something went wrong with the UDP client, peer: %s' % data[1])
                continue
            else:
                udp = threading.Thread(target=sct.udp_inf, args=(data, addr))
                udp.start()
                self.udpserss.sendto('rsp'.encode(), addr)
                print('Ping request received from peer %s' % int(data[1]))
        self.udpserss.close()


    def tcp_listen(self, port, sct):
        # establish a socket to endless listen
        serverSocket = socket(AF_INET, SOCK_STREAM)
        address = (LOCALHOST, port)
        serverSocket.bind(address)
        serverSocket.listen(MAXSOCKET)
        while 1:
            connectSocket, addr = serverSocket.accept()
            # connectSocket is a new socket to connect with client socket, and addr recv ip address and port
            # the initial socket (serverSocket) is used to wait for communication while the second is used to communicate.
            data = connectSocket.recv(BUFSIZE)
            # create a new thread to communicate with this client
            th = threading.Thread(target=sct.tcp_server, args=(connectSocket, addr, data))
            th.start()

    def tcp_client(self, port, msg=' '):
        # port is the destination, msg is the inf. the caller want send
        clientSocket = socket(AF_INET, SOCK_STREAM)
        addr = (LOCALHOST, port)
        try:
            clientSocket.connect(addr)
        except:
            print('can not connect to port: %s' % addr[1])
            return
        if type(msg) != bytes:
            msg = msg.encode()
        clientSocket.send(msg)
        data = clientSocket.recv(BUFSIZE)
        clientSocket.close()
        return data
        # return the info. recved to caller

class join_dht:
    def __init__(self, peer, known_peer):
        self.id = peer
        self.s1 = -1
        self.s2 = -1
        self.peerport = known_peer + PORTADD
        self.peerSocket = socket(AF_INET, SOCK_STREAM)
        self.comm = transmission(self.id)

    def tcp_join(self):
        msg = 'join %s' % self.id
        data = self.comm.tcp_client(self.peerport, msg).decode().split()
        try:
            data    # 'there s1 s2'
        except:
            # no data recved
            print('Something went wrong')
            sys.exit()
        else:
            self.s1 = int(data[1])
            self.s2 = int(data[2])
        self.peerSocket.close()

def input_command(node, stop_event):
    while 1:
        command = input()
        command = command.lower().split()
        if len(command) == 2 and command[0] == 'store':
            # print('Store %s' %command[1])
            if command[1].isdigit() and len(command[1]) == 4:
                filename = int(command[1])
                msg = 'store %s %s' % (hashfunction(filename), filename)
                node.communicate.tcp_client(node.sucsr1 + PORTADD, msg)
                print('Store %s request forwarded to my successor' % filename)
            else:
                print('invalid file name')

        elif len(command) == 2 and command[0] == 'request':
            filename = int(command[1])
            msg = 'request %s %s %s' % (hashfunction(filename), filename, node.id)
            print('File request for %s has been sent to my successor' % filename)
            node.communicate.tcp_client(node.sucsr1 + PORTADD, msg)

        elif len(command) == 1 and command[0] == 'quit':
            msg = 'quit %s %s %s' % (node.id, node.sucsr1, node.sucsr2)
            node.communicate.tcp_client(node.predr1 + PORTADD, msg)
            node.communicate.tcp_client(node.predr2 + PORTADD, msg)
            stop_event.set()
            sys.exit()
        else:
            print('Command invalid')
            continue

def hashfunction(filename):
    value = int(filename%256)
    return value

def main():
    # check the range of peer
    try:
        if sys.argv[1] == 'init':
            if len(sys.argv) != 6:
                print('Invalid arguments')
                sys.exit()
            node = peer_node(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))

        elif sys.argv[1] == 'join':
            if len(sys.argv) != 5:
                print('Invalid arguments')
                sys.exit()
            jnode = join_dht(int(sys.argv[2]), int(sys.argv[3]))
            jnode.tcp_join()
            node = peer_node(jnode.id, jnode.s1, jnode.s2, int(sys.argv[4]))
            print('Join request has been accepted')
            print('My first successor is Peer %d' %node.sucsr1)
            print('My second successor is Peer %d' %node.sucsr2)

    except:
        print('Invalid arguments')
        sys.exit()

    stop_event = threading.Event()

    inp = threading.Thread(target=input_command, args=(node,stop_event,))
    # why i have to put a comma here?
    sup = threading.Thread(target= node.send_ping)
    rup = threading.Thread(target= node.recv_ping)
    rtp = threading.Thread(target= node.tcp_lisn)

    inp.start()
    sup.start()
    rup.start()
    rtp.start()

if __name__ == '__main__':
    main()

