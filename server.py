import socket
import sys
import threading

# Some server settings
Host = '0.0.0.0'
Port = 1270

clients = []
usernames = []
colors = []
rooms = {'public': []} # Tracks who in each room
client_rooms = {} # Tracks who is in what room

# Will use ANSI escape codes for text coloring ^^
color_codes = {
    "black": "\033[38;5;232m",
    "white": "\033[38;5;231m",
    "pink": "\033[38;5;199m",
    "red": "\033[38;5;196m",
    "orange": "\033[38;5;214m",
    "yellow": "\033[38;5;226m",
    "green": "\033[38;5;40m",
    "cyan": "\033[38;5;51m",
    "light blue": "\033[38;5;81m",
    "blue": "\033[38;5;21m",
    "purple": "\033[38;5;93m"
}