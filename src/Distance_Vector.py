'''
Distance Vector class. Estimate in cost from source to all other destinations.

Also maintains important information pertinent to how the peer works. 
This class keeps track of when we last sent data to a particular peer and a
boolean specifying whether it is active.

@author: Emily Pakulski
'''

from socket import socket, AF_INET, SOCK_DGRAM
from sys import stdout
from time import strftime
import json

class Distance_Vector:
    
    def __init__(self, sender_ip, sender_port):
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.address = self.sender_ip + ':' + str(self.sender_port)
        self.destinations = {}
        self.is_neighbor = {}
    
    def get_weight(self, key):
        return self.destinations[key]
    
    def add_or_update_cost(self, key, weight, is_neighbor_bool):
        self.destinations[key] = weight
        self.is_neighbor[key] = is_neighbor_bool
        
    def send_distance_vector(self, dest_ip, dest_port, command):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(self.serialize(command), (dest_ip, dest_port))
 
    # updates distance vector following Bellman Ford equation using a neighbor's
    # distance vector.
    def compare_DVs(self, other_DV):
        for other_peer in other_DV.destinations:
            if other_peer != self.address:
                # distance from self to other_peer
                thru_weight = other_DV.destinations[other_peer] + \
                    other_DV.destinations[self.address]

                if not self.destinations.has_key(other_peer):
                    self.add_or_update_cost(other_peer, thru_weight, False)
                
                else:
                    if thru_weight < self.destinations[other_peer]:
                        self.add_or_update_cost(other_peer, thru_weight)

    ################### DATA TRANSFER METHODS ################################       
    # sends estimated distance of this node to all known destinations in JSON.
    def serialize(self, command):
        return json.dumps({'command' : command, \
                           'origin_ip' : self.sender_ip, \
                           'origin_port' : self.sender_port, \
                          'destinations' : self.destinations})
    
    @classmethod
    def parse(self, dv_string):
        deserialized = json.loads(dv_string)

        # initialize a new DV
        new_DV = Distance_Vector(deserialized['origin_ip'], deserialized['origin_port'])
        new_DV.destinations = deserialized['destinations']
        
        return new_DV
    
    # output human-readable version of distance vector
    def pretty_print(self):
        output = strftime('%H:%M:%S') + ' Distance vector list is: '
        
        for key in self.destinations:
            output += '\nDestination = ' + key + ', Cost = ' + \
            str(self.destinations[key]) + ', Link = ' + \
            self.sender_ip + ':' + str(self.sender_port)
        
        return output
        
