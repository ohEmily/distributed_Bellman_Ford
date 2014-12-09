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

from socket import socket, AF_INET, SOCK_DGRAM
from sys import argv, stdout, exit
from threading import Thread
from __builtin__ import raw_input
from datetime import datetime, timedelta

from Distance_Vector import Distance_Vector
from Neighbor import Neighbor
    
class Peer:
    local_IP = '127.0.0.1'
    BUFF_SIZE = 4096
    
    # commands for UI and keywords for the peer communication protocol
    link_down =     'LINKDOWN' 
    link_up =       'LINKUP'
    show_routes =   'SHOWRT'
    close =         'CLOSE'
    dv_update =     'UPDATE'

    ###################### STATIC METHODS #########################
    # pings the remote Google name server to get an external IP
    @staticmethod
    def get_external_ip(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        sockname = s.getsockname()[0]
        s.close()
        return str(sockname)

    @staticmethod
    def create_key(destination_ip, destination_port):
        return str(destination_ip) + ':' + str(destination_port)
    
    @staticmethod
    def parse_key(key):
        key_string = key.split(':') 
        return (key_string[0], int(key_string[1]))

    ############################ UI METHODS ###########################
    # loop serving as command-line interface for client machine
    def open_interface(self):
        while 1:
            message = raw_input().split()
            
            try:
                if len(message) >= 1:
                    if message[0].upper() == self.link_down:
                        if (len(message) >= 3):
                            print 'Remove link to ' + message[1] + ':' + message[2] + '. '
                            self.cmd_linkdown(message[1], message[2])
                        else:
                            print 'Missing arguments. '
                    elif message[0].upper() == self.link_up:
                        if (len(message) >= 3):
                            print 'Entered command: ' + self.link_up
                            self.cmd_linkup(message[1], message[2])
                        else:
                            print 'Missing arguments. '
                    elif message[0].upper() == self.show_routes:
                        self.cmd_showrt()
                    elif message[0].upper() == self.close:
                        self.cmd_close()
                    else:
                        print 'Command not found. '
            except Exception as e:
                print e
            
            stdout.flush()

    # allows user to destroy an existing link to its neighbor
    def cmd_linkdown(self, dest_ip, dest_port):
        key = Peer.create_key(dest_ip, dest_port)
        neighbor_obj = self.neighbors[key]
        neighbor_obj.is_active = False
    
    # reactivates link between existing link and its neighbor
    def cmd_linkup(self, dest_ip, dest_port):
        key = Peer.create_key(dest_ip, dest_port)
        neighbor_obj = self.neighbors[key]
        neighbor_obj.is_active = True

    # output a human-readable routing table
    def cmd_showrt(self):
        print self.distance_vector.pretty_print()
        stdout.flush()
        
    # close this process
    def cmd_close(self):
        try:
            exit(1) 
        except (KeyboardInterrupt, SystemExit):
            stdout.flush()
            print '\nPeer process shut down. '

    # returns true if we should send a distance vector to this client; false if not
    def should_send(self, neighbor_obj):
        
        if (neighbor_obj.is_active and neighbor_obj.send_count < 3):
            # DV has never been sent to this peer before
            if (neighbor_obj.last_active_time is 0):
                return True
            
            if (timedelta(datetime.now() - neighbor_obj.last_active_time).total_seconds >= self.timeout_seconds):
                return True
        
        return False

    # cycle through the current list of neighbors and continuously try to
    # send distance vectors.
    def send_DVs(self):
        while 1:
            for neighbor_name in self.neighbors:
                neighbor_obj = self.neighbors[neighbor_name]
                
                if neighbor_obj.is_active is True:
                    dest_ip, dest_port = Peer.parse_key(neighbor_name)
                    
                    if (self.should_send(neighbor_obj)):
                        self.distance_vector.send_distance_vector(dest_ip, dest_port, self.dv_update) # TODO
                    
                    # increment number of sends
                    neighbor_obj.send_count += 1
                    neighbor_obj.last_active_time = datetime.now()

    # waits to hear for a new peer. If we hear from a new peer, try to send_update
    # the distance vector.
    def handle_incoming_data(self, data, peer_ip, peer_port):
        keyword = data.split(' ', 1)[1]
        
        if (keyword is self.dv_update):
            Distance_Vector.parse(data, peer_ip, peer_port)
        
        print 'Received DV from ' + str(peer_ip) + ':' + str(peer_port) + '.'

    # Add to neighbor dictionary and add to Distance Vector
    def add_neighbor(self, remote_ip, remote_port, remote_weight):
#         print remote_ip + ' ' + str(remote_port) + ' ' + str(remote_weight)
#         stdout.flush()
        key = Peer.create_key(remote_ip, remote_port)
        self.neighbors[key] = Neighbor(True, 0, 0)
        
        self.distance_vector.add_or_update_cost(key, remote_weight)

    def __init__(self, argv):
        self.local_port = int(argv[1])
        self.timeout_seconds = int(argv[2])
        self.neighbors = {}
        self.distance_vector = Distance_Vector(self.local_IP, self.local_port)
        #print 'my ip is ' + Peer.get_external_ip()
        
        # register neighbors passed in as arguments: initialization step of algorithm
        for n in range(3, len(argv) - 2, 3):
            self.add_neighbor(argv[n], int(argv[n + 1]), int(argv[n + 2]))
        
        # open command line interface
        interface_thread = Thread(target=self.open_interface, args=())
        interface_thread.start()
        
        # send updated distance vectors to neighbors
        sending_thread = Thread(target=self.send_DVs, args=())
        sending_thread.start()
               
        # set up read-only UDP socket to listen for incoming messages
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((self.local_IP, self.local_port))
        # continuously receive data from neighbors, updating distance vector 
        # and neighbor list accordingly
        while 1:
            data, addr = sock.recvfrom(self.BUFF_SIZE) 

            client_thread = Thread(target=self.handle_incoming_data, 
                            args=(data, addr[0], addr[1]))
            client_thread.start()
        
def main(argv):
    Peer(argv)
    
main(argv)