'''
Distance Vector class. Estimate in cost from source to all other destinations.

Also maintains important information pertinent to how the peer works. 
This class keeps track of when we last sent data to a particular peer and a
boolean specifying whether it is active.

@author: Emily Pakulski
'''

from socket import socket, AF_INET, SOCK_DGRAM
from sys import stdout
from datetime import datetime
from time import strftime

class Distance_Vector:
    def __init__(self, sender_ip, sender_port):
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.destinations = {}
    
    def get_weight(self, key):
        return self.destinations[key]
    
    def add_or_update_cost(self, key, weight):
        self.destinations[key] = weight
        
    def send_distance_vector(self, dest_ip, dest_port, command):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(command + '\n' + self.serialize(), (dest_ip, dest_port))
 
    # sends estimated distance of this node to all known destinations in
    # format that matches the parsing method below.
    #
    # format: '<ip:port> <weight> \n' for each entry in dictionary
    def serialize(self):
        output = ''
        
        for key in self.destinations:
            output += key + ' ' + str(self.destinations[key]) + '\n'
            
        print 'test of vector string: ' + output + '\n'
        stdout.flush()
        
        return output
    
    @classmethod
    def parse(self, dv_string, source_ip, source_port):
        # initialize a new DV
        new_DV = Distance_Vector(source_ip, source_port)
        
        # skip the first line because that contains the command
        values_array = dv_string.split('\n')[1:] 
        
#         for i in range(0, len(values_array)):
#             line = values_array[i].split()
#             
#             (destination_ip, destination_port) = Peer.parse_key(line[0])
#             
#             new_DV.add_or_update_cost(destination_ip, destination_port, line[1])
            
        return new_DV
    
    # output human-readable version of distance vector
    def pretty_print(self):
        output = strftime('%H:%M:%S') + ' Distance vector list is: '
        
        for key in self.destinations:
            output += '\nDestination = ' + key + ', Cost = ' + \
            str(self.destinations[key]) + ', Link = ' + \
            self.sender_ip + ':' + str(self.sender_port)
        
        return output
        
