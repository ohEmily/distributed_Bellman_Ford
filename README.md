Distributed Bellman-Ford (Python)
=================================
An implementation of a distributed routing algorithm based on the Bellman Ford 
equation. Uses distance vectors to dynamically recalculate shortest paths as 
network topography changes.

Extra Features
--------------
 - added command: view next hop data (type 'shownxt')

Description of Inter-Peer Communication Protocol
------------------------------------------------
Peers communicate using an object serialized to JSON. The object always has a 'command' attribute which tells the receiving peer what sort of payload it is receiving. From there, depending on what kind of message it received (SHOWRT, LINKUP, or LINKDOWN), it reads different parts of the JSON object pertinent to that command.

If the distance vector is being sent, it sends both the weights and the next hops.
 
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