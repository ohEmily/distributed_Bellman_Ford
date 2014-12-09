'''
Peer in distributed Bellman Ford algorithm implementation. Each peer has an
instance of the Distance_Vector class.

Run using 'python Peer.py <local_port> <timeout_seconds> 
    <<remote_ip_1> <remote_port_1> <remote_weight_1>>
    <<remote_ip_2> <remote_port_2> <remote_weight_2>>' ...etc. 
    for any number of remote clients. 
    
E.g. 'python Peer.py 55555 3 127.0.0.1 55556 15 127.0.0.1 55557 
    20 127.0.0.1 55558 25'

@author: Emily Pakulski
'''

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from sys import argv, stdout
from threading import Thread
from __builtin__ import raw_input
from Distance_Vector import Distance_Vector
    
class Peer:
    local_IP = '127.0.0.1'
    BUFF_SIZE = 4096
    
    # commands for UI and keywords for the peer communication protocol
    link_down = 'LINKDOWN'
    link_up = 'LINKUP'
    show_routes = 'SHOWRT'
    close = 'CLOSE'
    dv_update = 'UPDATE'

    # pings the remote Google name server to get an external IP
    def get_external_ip(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        sockname = s.getsockname()[0]
        s.close()
        return str(sockname)
    
    # cycle through the current list of destinations and continuously try to
    # send distance vectors.
    def send_DVs(self):
        while 1:
            self.distance_vector.send_update(self.timeout_seconds, self.dv_update)

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

    # waits to hear for a new peer. If we hear from a new peer, try to send_update
    # the distance vector.
    def handle_message_to_peer(self, data, peer_ip, peer_port):
        keyword = data.split()[0]
        
        if (keyword is self.dv_update):
            Distance_Vector.parse_distance_vector(data, peer_ip, peer_port)
        
        print 'Received DV from ' + str(peer_ip) + ':' + str(peer_port) + '.'

    # send remote peer edge weight, and upon confirmation that the weight was
    # received, store that data in this node's routing table
    def add_neighbor(self, remote_ip, remote_port, remote_weight):
        print remote_ip + ' ' + str(remote_port) + ' ' + str(remote_weight)
        
        self.distance_vector.add_cost(remote_ip, remote_port, remote_weight)
         
        print 'New peer connected on '  + str(remote_ip) + ':' + str(remote_port) + '. '
        stdout.flush()

    def __init__(self, argv):
        self.local_port = int(argv[1])
        self.timeout_seconds = int(argv[2])
        self.distance_vector = Distance_Vector(self.local_IP, self.local_port)
        print 'my ip is ' + self.get_external_ip()
        
        # register neighbors passed in as arguments: initialization step of algorithm
        for n in range(3, len(argv) - 2, 3):
            self.add_neighbor(argv[n], int(argv[n + 1]), int(argv[n + 2]))
       
        # set up read-only UDP socket to listen for incoming messages
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((self.local_IP, self.local_port))

        # open command line interface
        interface_thread = Thread(target=self.open_interface, args=())
        interface_thread.start()
        
        # continuously cycle through peers and send updated distance vector
        sending_thread = Thread(target=self.send_DVs, args=())
        sending_thread.start()
        
        # send_update distance vector with any data received from peers
        while 1:
            data, addr = sock.recvfrom(self.BUFF_SIZE) 
             
            client_thread = Thread(target=self.handle_message_to_peer, 
                            args=(data, addr[0], addr[1]))
            client_thread.start()
        
def main(argv):
    Peer(argv)
    
main(argv)