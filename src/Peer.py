'''
Peer. 

Run using 'python Peer.py <local_port> <timeout_seconds> 
    <<remote_ip_1> <remote_port_1> <remote_weight_1>>
    <<remote_ip_2> <remote_port_2> <remote_weight_2>>' ...etc. 
    for any number of remote clients. 
    
E.g. 'python Peer.py 55555 3 127.0.0.1 55556 15 127.0.0.1 55557 20 127.0.0.1 55558 25'

@author: Emily Pakulski
'''

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from sys import argv, stdout
from threading import Thread
from __builtin__ import raw_input
from Distance_Vector import Distance_Vector
    
class Peer:
    local_IP = '127.0.0.1'
    
    # commands for UI
    link_down = 'LINKDOWN'
    link_up = 'LINKUP'
    show_routes = 'SHOWRT'
    close = 'CLOSE'

    # loop serving as command-line interface for client machine
    def open_interface(self):
        while 1:
            message = raw_input().split()
            print "Print command for testing: " + str(message[0:])
            
            if message[0] == self.link_down:
                print self.link_down
            if message[0] == self.link_up:
                print self.link_up
            if message[0] == self.show_routes:
                print self.show_routes
            if message[0] == self.close:
                print self.close

    # waits to hear for a new peer
    def update_peer(self, peer_socket, peer_ip, peer_port):        
        while 1:
            # parse peer message
            weight = peer_socket.recv() 
            print 'Weight received from ' + str(peer_ip) + ': ' + weight
            
            #self.routing_table[peer_ip] = (int(weight), peer_socket)

    def write_dv_to_routing_table(self, distance_vector, is_active, timestamp):
        key = distance_vector.sender_ip + ':' + distance_vector.sender_port + '-' \
            + distance_vector.dest_ip + ':' + distance_vector.dest_ip
            
        self.routing_table[key] = (distance_vector, is_active, timestamp)

    # send remote peer edge weight, and upon confirmation that the weight was
    # received, store that data in this node's routing table
    def connect_to_new_peer(self, remote_ip, remote_port, remote_weight):
        print remote_ip + ' ' + str(remote_port) + ' ' + str(remote_weight)
        
        remote_sock = socket(AF_INET, SOCK_STREAM)
        remote_sock.connect((remote_ip, remote_port))
        
        distance_vector = Distance_Vector(remote_weight, self.local_IP, \
                                          self.local_port, remote_ip, remote_port)
        remote_sock.sendall(distance_vector.stringify())
        
        self.write_dv_to_routing_table(distance_vector)
        
        print 'New peer connected on '  + str(remote_ip) + ':' + str(remote_port) + '. '
        stdout.flush()

    def __init__(self, argv):
        self.local_port = int(argv[1])
        self.timeout_seconds = int(argv[2])
        
        # maps each IP to tuple of (weight, socket)
        self.routing_table = {}
        
        # connect to peers passed in as arguments: initialization step of algorithm
        for n in range(3, len(argv) - 2, 3):
            self.connect_to_new_peer(argv[n], int(argv[n + 1]), int(argv[n + 2]))      
       
        # set up read-only UDP socket to listen for incoming messages
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((self.local_IP, self.local_port))
    
        # open command line interface
        interface_thread = Thread(target=self.open_interface, args=())
        interface_thread.start()
        
        # continuously cycle through peers and send updated distance vectors
        while 1:
            client_connection, addr = sock.accept()
            
            client_thread = Thread(target=self.update_peer, 
                            args=(client_connection, addr[0], addr[1]))
            client_thread.start()
        
def main(argv):
    Peer(argv)
    
main(argv)