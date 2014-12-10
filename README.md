Distributed Bellman-Ford (Python)
=================================
An implementation of a distributed routing algorithm based on the Bellman Ford 
equation. Uses distance vectors to dynamically recalculate shortest paths as 
network topography changes.

Note: to show the value for infinity in this assignment, I used 'maxint', which in Python is 2147483647.

Extra Features
--------------
 - added command: force sending DV to peer (type 'update <ip_addr> <port>')

Inter-Peer Communication Protocol
---------------------------------
Peers communicate using JSON. 
 
How to run (example)
----------

Terminal 1:
```
python Peer.py 55555 3 192.168.0.106 55556 5
```

Terminal 2:
```
python Peer.py 55556 3 192.168.0.106 55555 5
```

In order for the Peer you started up first not to simply remove all the peers passed in
as arguments from its routing table because they are not responding, the other peer
process(es) must be started within 3 * timeout seconds.