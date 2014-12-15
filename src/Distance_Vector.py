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
        self.next_hops = {}
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
    
    def add_or_update_cost(self, key, weight, next_hop):
        self.destination_weights[key] = weight
        self.next_hops[key] = next_hop
        
    def send_distance_vector(self, dest_ip, dest_port, command):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(self.serialize(command), (dest_ip, dest_port))
 
    # updates distance vector following Bellman Ford equation using a neighbor's
    # distance vector.
    def compare_DVs(self, other_DV):
        updated_DV = False
        changed_next_hops = []
        
        for other_peer_key in other_DV.destination_weights:
            if other_peer_key != self.address:
                # distance from self to other_peer_key
                thru_weight = other_DV.destination_weights[other_peer_key] + \
                    other_DV.destination_weights[self.address]

                if not self.destination_weights.has_key(other_peer_key):
                    self.add_or_update_cost(other_peer_key, thru_weight, other_DV.address)
                    updated_DV = True
                
                else: # if we already had this node in the neighbor list
                    if thru_weight < self.destination_weights[other_peer_key]:
                        self.add_or_update_cost(other_peer_key, thru_weight, other_DV.address)
                        updated_DV = True
                        changed_next_hops.append(other_DV.address)
                        
            else: # if other_peer's neighbor == this peer
                if other_DV.destination_weights[self.address] < self.destination_weights[other_DV.address]:
                    self.destination_weights[other_DV.address] = other_DV.destination_weights[self.address]
                    updated_DV = True
                    changed_next_hops.append(other_DV.address)
        
        if updated_DV:
            self.check_next_hops(changed_next_hops)
        
        return updated_DV

    def check_next_hops(self, changed_next_hops):
        print 'updated DV. hops changed: ' + str(changed_next_hops)
        for each_hop in changed_next_hops:
            for each_destination in self.destination_weights.keys():
                if self.next_hops[each_destination] == each_hop:
                    self.destination_weights[each_destination] = float('inf')

    ################### DATA TRANSFER METHODS ################################       
    # sends estimated distance of this node to all known destination_weights in JSON.
    def serialize(self, command):
        return json.dumps({'command' : command, \
                           'origin_ip' : self.sender_ip, \
                           'origin_port' : self.sender_port, \
                          'destination_weights' : self.destination_weights, \
                          'next_hops' : self.next_hops })
    
    @classmethod
    def parse(self, dv_string):
        deserialized = json.loads(dv_string)

        # initialize a new DV
        new_DV = Distance_Vector(deserialized['origin_ip'], deserialized['origin_port'])
        new_DV.destination_weights = deserialized['destination_weights']
        new_DV.next_hops = deserialized['next_hops']
        
        return new_DV
    
    # output human-readable version of distance vector
    def pretty_print(self):
        output = strftime('%H:%M:%S') + ' Distance vector list is: '
        
        for key in self.destination_weights:
            output += '\nDestination = ' + key + ', Cost = ' + \
            str(self.destination_weights[key]) + ', Link = ' + \
            self.sender_ip + ':' + str(self.sender_port)
        
        return output
    
    def pretty_print_next_hops(self):
        output = strftime('%H:%M:%S') + ' Distance vector list is: '
        
        for key in self.destination_weights:
            output += '\nDestination = ' + key + ', Next hop = ' + \
            str(self.next_hops[key]) + ', Link = ' + \
            self.sender_ip + ':' + str(self.sender_port)
        
        return output
