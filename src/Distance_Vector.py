'''
Distance Vector class. Estimate in cost from source to all other destinations.

Also maintains important information pertinent to how the peer works. 
This class keeps track of when we last sent data to a particular peer and a
boolean specifying whether it is active.

@author: Emily Pakulski
'''

import sys
from sys import stdout
from datetime import datetime

class Distance_Vector:
    
    def __init__(self, sender_ip, sender_port):
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.destinations = {}
        
        # add self to destinations dictionary TODO not necessary? 
        #key = self.create_key(sender_ip, sender_port)
        #self.destinations[key] = 0
    
    def create_key(self, destination_ip, destination_port):
        return str(destination_ip) + ':' + str(destination_port)
    
    def parse_key(self, key):
        key_string = key.split(':') 
        return (key_string[0], key_string[1])
    
    def add_cost(self, destination_ip, destination_port, weight):
        key = self.create_key(destination_ip, destination_port)
        self.destinations[key] = (weight, True, 0)
    
    def linkdown(self, destination_ip, destination_port):
        key = self.create_key(destination_ip, destination_port)
        value = self.destinations[key]
        value[1] = False
        self.destinations[key] = value
    
    def get_destinations(self):
        return self.destinations.keys()
    
    def get_value(self, key):
        return self.destinations[key]
    
    # sends estimated distance of this node to all known destinations in
    # format that matches the parsing method below.
    #
    # format: '<ip:port> <weight> \n' for each entry in dictionary
    def stringify(self):
        output = ''
        
        for key in self.destinations:
            output += key + ' ' + self.destinations[key][0] + '\n'
            
        return output
    
    # 
    @classmethod
    def parse_distance_vector(self, dv_string, source_ip, source_port):
        # initialize a new DV
        new_DV = Distance_Vector(source_ip, source_port)
        
        values_array = dv_string.split('\n')
        
        for i in range(0, len(values_array)):
            line = values_array[i].split()
            
            (destination_ip, destination_port) = self.parse_key(line[0])
            
            new_DV.add_cost(destination_ip, destination_port, line[1])
            
        return new_DV
