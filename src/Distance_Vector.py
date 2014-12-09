'''
Distance Vector class. Estimate in cost from source to all other destinations.

Also maintains important information pertinent to how the peer works. 
This class keeps track of when we last sent data to a particular peer and a
boolean specifying whether it is active.

@author: Emily Pakulski
'''

from socket import socket, AF_INET, SOCK_DGRAM
from sys import stdout
from datetime import datetime, timedelta
from Entry import Entry

class Distance_Vector:
    
    def __init__(self, sender_ip, sender_port):
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.destinations = {}
    
    def get_entry(self, key):
        return self.destinations[key]
    
    def create_key(self, destination_ip, destination_port):
        return str(destination_ip) + ':' + str(destination_port)
    
    def parse_key(self, key):
        key_string = key.split(':') 
        return (key_string[0], int(key_string[1]))
    
    def add_cost(self, destination_ip, destination_port, weight):
        key = self.create_key(destination_ip, destination_port)
        
        self.destinations[key] = Entry(weight, True, 0, 0)
        
    def linkdown(self, destination_ip, destination_port):
        key = self.create_key(destination_ip, destination_port)
        value = self.destinations[key]
        value.is_active = False
        self.destinations[key] = value
    
    def send_distance_vector(self, dest_ip, dest_port, command):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.sendto(command + '\n' + self.stringify(), (dest_ip, dest_port))

    # returns true if we should send a distance vector to this client; false if not
    def should_send(self, key, timeout):
        this_entry = self.destinations[key] 
        
        if (this_entry.send_count < 3):
            # if has never been sent to this peer before
            if (this_entry.last_active_time is 0):
                return True
            
            if (datetime.now() - this_entry.last_active_time \
                >= timedelta(seconds = timeout)):
                return True
        
        return False

    # cycle through all current neighbors and update times
    def send_update(self, timeout, command):
        for key in self.destinations:            
            # if link being up is set to TRUE
            if (self.destinations[key].is_active is True):
                dest_ip, dest_port = self.parse_key(key)
                
                if (self.should_send(key, timeout)): # we've never sent anything to this peer
                    self.send_distance_vector(dest_ip, dest_port, command)
                    
                    # increment number of sends
                    self.destinations[key].send_count += 1
                    self.destinations[key].last_active_time = datetime.now()
                    
    # sends estimated distance of this node to all known destinations in
    # format that matches the parsing method below.
    #
    # format: '<ip:port> <weight> \n' for each entry in dictionary
    def stringify(self):
        output = ''
        
        for key in self.destinations:
            output += key + ' ' + str(self.destinations[key].weight) + '\n'
            
        print 'test of vector string: ' + output + '\n'
        stdout.flush()
        
        return output
    
    @classmethod
    def parse_distance_vector(self, dv_string, source_ip, source_port):
        # initialize a new DV
        new_DV = Distance_Vector(source_ip, source_port)
        
        # skip the first line because that contains the command
        values_array = dv_string.split('\n')[1:] 
        
        for i in range(0, len(values_array)):
            line = values_array[i].split()
            
            (destination_ip, destination_port) = self.parse_key(line[0])
            
            new_DV.add_cost(destination_ip, destination_port, line[1])
            
        return new_DV
