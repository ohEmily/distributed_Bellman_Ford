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

BUFF_SIZE = 4096
local_IP = '127.0.0.1'
BACKLOG = 5

# Connects to server socket and starts send and receive threads.
def main(argv):
    local_port_no = int(argv[1])
    timeout_seconds = int(argv[2])
    
    # maps IPs to tuple of (weight, socket)
    routing_table = {}
    
    # connect to peers passed in as arguments
    for n in range(3, len(argv) - 2, 3):
        remote_ip = argv[n]
        remote_port = argv[n + 1]
        remote_weight = argv[n + 2]
        
        remote_sock = socket(AF_INET, SOCK_STREAM)
        remote_sock.connect((remote_ip,remote_port))
        
        routing_table[remote_ip] = (remote_weight, remote_sock)
        
        #print argv[n] + ' ' + argv[n + 1] + ' ' + argv[n + 2]
   
    # listen for more
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind((local_IP, local_port_no))
    sock.listen(BACKLOG)

    while 1:
        client_connection, addr = sock.accept()
        print 'New peer connected on '  + str(addr[0]) + ':' + str(addr[1]) + '. '
        stdout.flush()
        #thread = Thread(target=handle_client, args=(client_connection, addr))
        #thread.start()
    
    
main(argv)