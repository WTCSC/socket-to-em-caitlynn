import socket
import threading
import random
# import pickle (or similar module - would prefer something a little bit safer)

class Monopoly_Server:
    # Change host as needed
    def __init__(self, host='0.0.0.0', port='1270'):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(host, port) # <<< Double check this line
        self.server.listen(4)
        self.clients = []
        self.players = {}
        self.usernames = set()
        self.current_turn = 0
        self.starting_money = 1500 # <<< Can adjust as wanted
        self.properties = self.init_properties()
        self.board_size = 40 # <<< Can adjust as wanted

    def init_properties(self):
        properties = {}
        for i in range(1,40):
            if i % 5 == 0:
                properties[i] = {
                    'name': f'property {i}', # <<< Randomize property names if ur feeling fancy
                    'price': 150 + (i * 10), # <<< Can adjust as wanted
                    'rent': 25 + (i * 5), # <<< Can adjust as wanted
                    'owner': None
                }
        return properties