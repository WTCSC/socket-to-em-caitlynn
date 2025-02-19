import socket
import sys
import threading

# Some server settings
Host = '0.0.0.0'
Port = 1270

username = input("Enter your username:")

# Establish the server connection
Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Client.connect((Host, Port))