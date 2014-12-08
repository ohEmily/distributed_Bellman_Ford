'''
Distance Vector class. 

@author: Emily Pakulski
'''

import sys
from sys import stdout

class Distance_Vector:
    
    def __init__(self, weight, sender_ip, sender_port, dest_ip, dest_port):
        self.weight = weight
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
    
    def stringify(self):
        return str(self.weight) + '\n' \
            + str(self.sender_ip) + '\n' \
            + str(self.sender_port) + '\n' \
            + str(self.dest_ip) + '\n' \
            + str(self.dest_port) + '\n'
    
    @classmethod
    def parse_distance_vector(self, dv_string):
        values_array = dv_string.split()
        self.weight = values_array[0]
        self.sender_ip = values_array[1]
        self.sender_port = values_array[2]
        self.dest_ip = values_array[3]
        self.dest_port = values_array[4]
        
        return self
