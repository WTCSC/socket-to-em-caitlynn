import socket
#import pickle (or similar module - would prefer something a little bit safer)

class Monopoly_Client:
    # Change host as needed
    def __init__(self, host='127.0.0.1', port='1270'):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(host, port)
        self.username = None
        self.starting_money = 0
        self.my_turn = False