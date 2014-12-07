'''
Peer. 

Run using 'python Peer.py <local_port> <timeout_seconds> 
    <<remote_ip_1> <remote_port_1> <remote_weight_1>>
    <<remote_ip_2> <remote_port_2> <remote_weight_2>>' ...etc. 
    for any number of remote clients. 
    
E.g. 'python Peer.py 55555 3 127.0.0.1 55556 127.0.0.1 555557 127.0.0.1 555558'

@author: Emily Pakulski
'''

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from sys import argv, stdout, exit
from threading import Thread
from __builtin__ import raw_input
    
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

    def handle_new_peer(self, peer_socket, peer_ip, peer_port):
        print 'New peer connected on '  + str(peer_ip) + ':' + str(peer_port) + '. '
        stdout.flush()
        
        # parse peer message
        
        self.routing_table[peer_ip] = ()

    # attempt to connect. If successful, return true, else don't connect.
    def confirm_connection(self, remote_sock):
        remote_sock.sendall('IP: ' + self.local_IP \
                            + 'Port: ' + self.local_port \
                            + 'Weight: ' + 5)
        
        # if gets confirmation within timeout_seconds
        
        return True

    def connect_to_peer(self, remote_ip, remote_port, remote_weight):
        remote_sock = socket(AF_INET, SOCK_STREAM)
        remote_sock.connect((remote_ip, remote_port))
        
        if (self.confirm_connection(remote_sock) is True):
            self.routing_table[remote_ip] = (remote_weight, remote_sock)
        
        #print remote_ip + ' ' + remote_port + ' ' + remote_weight

    def __init__(self, argv):
        self.local_port = int(argv[1])
        self.timeout_seconds = int(argv[2])
        
        # maps each IP to tuple of (weight, socket)
        self.routing_table = {}
        
        # connect to peers passed in as arguments
        for n in range(3, len(argv) - 2, 3):
            self.connect_to_peer(argv[n], int(argv[n + 1]), argv[n + 2])      
       
        # set up read-only UDP socket to listen for incoming messages
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((self.local_IP, self.local_port))
    
        # open command line interface
        interface_thread = Thread(target=self.open_interface, args=())
        interface_thread.start()
    
        while 1:
            client_connection, addr = sock.accept()
            
            client_thread = Thread(target=self.handle_new_peer, 
                            args=(client_connection, addr[0], addr[1]))
            client_thread.start()
        
def main(argv):
    Peer(argv)
    
main(argv)