'''
Peer. 

Run using 'python Peer.py <local_port_no> <timeout_seconds> 
    <<remote_ip_1> <remote_port_1> <remote_weight_1>>' for any number
    of remote clients. 

@author: Emily Pakulski
'''

from socket import socket, AF_INET, SOCK_STREAM
from sys import argv, stdout, exit
from threading import Thread
    
class Peer:
    local_IP = '127.0.0.1'
    BACKLOG = 5

    def handle_new_peer(self, peer_socket, peer_ip, peer_port):
        print 'New peer connected on '  + str(peer_ip) + ':' + str(peer_port) + '. '
        stdout.flush()

    def connect_to_peer(self, remote_ip, remote_port, remote_weight):
        remote_sock = socket(AF_INET, SOCK_STREAM)
        remote_sock.connect((remote_ip,remote_port))

        self.routing_table[remote_ip] = (remote_weight, remote_sock)
        
        #print remote_ip + ' ' + remote_port + ' ' + remote_weight

    def __init__(self, argv):
        local_port_no = int(argv[1])
        self.timeout_seconds = int(argv[2])
        
        # maps each IP to tuple of (weight, socket)
        self.routing_table = {}
        
        # connect to peers passed in as arguments
        for n in range(3, len(argv) - 2, 3):
            self.connect_to_peer(argv[n], argv[n + 1], argv[n + 2])      
       
        # listen for more
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((self.local_IP, local_port_no))
        sock.listen(self.BACKLOG)
    
        while 1:
            client_connection, addr = sock.accept()
            
            thread = Thread(target=self.handle_new_peer, 
                            args=(client_connection, addr[0], addr[1]))
            thread.start()
        
def main(argv):
    Peer(argv)
    
main(argv)