# 9311asst
# python version: python3

This work is a P2P Network using Distributed Hash Table.

By typing: python3 p2p.py init <peer> <first_successor> <second_successor> <ping_interval> you can initialize the network
where:
PEER - Peer ID
FIRST SUCCESSOR - Id of first successor
SECOND SUCCESSOR -Id of second successor
PING INTERVAL - How often you send the ping messages

by typing: python3 p2p.py join <peer> <known_peer> <ping_interval> you can let the new peer join to existing network

When you are running the program, you can type the following commands in the terminal:

store <filename> - store a file in the network

request <filename> - retriveval a file in the network

qiut - leave the network

Note: the file name can be only 4 digits.

