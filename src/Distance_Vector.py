'''
Distance Vector class. Estimate in cost from source to all other destination_weights.

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
        self.destination_weights = {}
        self.previous_weights = {}
    
    def deactivate_link(self, key):
        self.previous_weights[key] = self.destination_weights[key]
        self.destination_weights[key] = float('inf')

    def reactivate_link(self, key):
        self.destination_weights[key] = self.previous_weights[key]
        
    def set_weight(self, key, weight):
        self.destination_weights[key] = weight
    
    def get_weight(self, key):
        return self.destination_weights[key]
    
    def add_or_update_cost(self, key, weight):
        self.destination_weights[key] = weight
        
    def send_distance_vector(self, dest_ip, dest_port, command):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(self.serialize(command), (dest_ip, dest_port))
 
    # updates distance vector following Bellman Ford equation using a neighbor's
    # distance vector.
    def compare_DVs(self, other_DV):
        for other_peer_key in other_DV.destination_weights:
            if other_peer_key != self.address:
                # distance from self to other_peer_key
                thru_weight = other_DV.destination_weights[other_peer_key] + \
                    other_DV.destination_weights[self.address]

                if not self.destination_weights.has_key(other_peer_key):
                    self.add_or_update_cost(other_peer_key, thru_weight)
                
                else: # if we already had this node in the neighbor list
                    if thru_weight < self.destination_weights[other_peer_key]:
                        self.add_or_update_cost(other_peer_key, thru_weight)
            else: # if other_peer's neighbor == this peer
                if other_DV.destination_weights[self.address] < self.destination_weights[other_DV.address]:
                    self.destination_weights[other_DV.address] = other_DV.destination_weights[self.address]


    ################### DATA TRANSFER METHODS ################################       
    # sends estimated distance of this node to all known destination_weights in JSON.
    def serialize(self, command):
        return json.dumps({'command' : command, \
                           'origin_ip' : self.sender_ip, \
                           'origin_port' : self.sender_port, \
                          'destination_weights' : self.destination_weights})
    
    @classmethod
    def parse(self, dv_string):
        deserialized = json.loads(dv_string)

        # initialize a new DV
        new_DV = Distance_Vector(deserialized['origin_ip'], deserialized['origin_port'])
        new_DV.destination_weights = deserialized['destination_weights']
        
        return new_DV
    
    # output human-readable version of distance vector
    def pretty_print(self):
        output = strftime('%H:%M:%S') + ' Distance vector list is: '
        
        for key in self.destination_weights:
            output += '\nDestination = ' + key + ', Cost = ' + \
            str(self.destination_weights[key]) + ', Link = ' + \
            self.sender_ip + ':' + str(self.sender_port)
        
        return output
