# PEER TO PEER NETWORK USING DISTRIBUTED HASH TABLE
# python3
# version 2.0

This program implements a Peer-to-Peer Network using Distributed Hash Table, which is confined to a single operating system with sockets or processes acting as independent peers. There are five P2P servivces in this program, including data insertion, data retrieval, peer joining, peer departure (graceful) and Peer departure (abrupt).

Updated:
-fixed the problem that some threads keep running after the process is terminated
-fixed the issue that sometime it does not raise Exception in the main function, which may led this program can not run on CSE Linux.
-add init.sh to set up processes
-limit the range of the peer ID
-if there is no a file which a peer reqest, the relatied node will print: no such file

How to use:
1. Run the init.sh file to initialize the network, which will run 7 peers.

2. You can also initialize the network with your own peers, the command is:

python3 p2p.py <TYPE> <PEER> <FIRST_SUCCESSOR> <SECOND_SUCCESSOR> <PING_INTERVAL>

TYPE - Type of run, here is 'init'
PEER - Peer ID, which can only be [0,255]
FIRST_SUCCESSOR - Id of first successor
SECOND_SUCCESSOR -Id of second successor
PING_INTERVAL (seconds) -  How often you send the ping messages

The port number of each peer is PORTADD + PEER_ID, you can change the PORTADD in the p2p.py.

As an instance, you can run 'python3 p2p.py init 2 4 5 30' to start a peer whose id is 2 and successors are 4 and 5. It will send ping every 30 seconds.

3. A new peer can also approach any of the existing peers to join the DHT, the command is:

python3 p2p.py <TYPE> <PEER> <KNOWN_PEER> <PING_INTERVAL> 

TYPE - Type of run, here is 'join'
PEER - Peer ID, which can only be [0,255]
KNOWN_PEER - Id of the peer it knows
PING_INTERVAL (seconds) -  How often you send the ping messages

4. When you are running the process, you can type 'store <filename>' to store a file in the DHT. 

But just a reminder that filenames can be only four-digit numbers such as 0000, 0159, 1890, etc. Filenames such as a912 and
32134 are invalid because the former contains a non-numeral character and the latter does not consist of exactly 4 numerals.

5. you can request any peer to retrieve a data record from the
DHT in a running process by typing 'request <filename>'

6. If you want to A peer gracefully leave the DHT by announcing its
departure to other relevant peers before shutting down, you can type 'quit'.
