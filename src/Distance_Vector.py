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
import json

class Distance_Vector:
    DIST_INFINITY = -1
    
    
    def __init__(self, sender_ip, sender_port):
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.destinations = {}
        self.is_neighbor = {}
    
    def get_weight(self, key):
        return self.destinations[key]
    
    def add_or_update_cost(self, key, weight, is_neighbor_bool):
        if not self.destinations.has_key(key):
            self.destinations[key] = weight
            self.is_neighbor[key] = is_neighbor_bool
        
        
        
        
    def send_distance_vector(self, dest_ip, dest_port, command):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(self.serialize(command), (dest_ip, dest_port))
 
    # updates distance vector following Bellman Ford equation using another
    # distance vector.
    def compare_DVs(self, other_DV):
        for peer_from_other_DV in other_DV.destinations:
            thru_weight = other_DV.destinations[peer_from_other_DV] + \
                other_DV.destinations[self.sender_ip + ':' + self.sender_port]
            
            if not self.destinations.has_key(peer_from_other_DV):
                self.add_or_update_cost(peer_from_other_DV, thru_weight)
            
            else:
                if thru_weight < self.destinations[peer_from_other_DV]:
                    self.add_or_update_cost(peer_from_other_DV, thru_weight)
                
    # sends estimated distance of this node to all known destinations in JSON.
    def serialize(self, command):
        return command + ' \n' + json.dumps(self.destinations)
    
    @classmethod
    def parse(self, dv_string, source_ip, source_port):
        # initialize a new DV
        new_DV = Distance_Vector(source_ip, source_port)
        
        # skip the first line because that contains the command
        values_json = dv_string.split('\n', 1)[1]

        new_DV.destinations = json.loads(values_json)
            
        return new_DV
    
    # output human-readable version of distance vector
    def pretty_print(self):
        output = strftime('%H:%M:%S') + ' Distance vector list is: '
        
        for key in self.destinations:
            output += '\nDestination = ' + key + ', Cost = ' + \
            str(self.destinations[key]) + ', Link = ' + \
            self.sender_ip + ':' + str(self.sender_port)
        
        return output
        
