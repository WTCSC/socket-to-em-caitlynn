import socket
import sys
import threading
from loguru import logger

# Configuring Loguru for clean loggin
logger.remove()

# Wrotes anything that is log level INFO or higher to the terminal (can be changed)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
) 

# Writes all debug logs to a log file (capped at 500KB and only kept for a week)
logger.add("server.log", rotation="500 KB", retention="7 Days", level="DEBUG") 

class Server:

    host = '127.0.0.1'
    port = 1270

    # Color code dictionary with all the ANSI escape codes for name coloring
    color_codes = {
        "black": "\033[38;5;232m",
        "white": "\033[38;5;231m",
        "pink": "\033[38;5;199m",
        "red": "\033[38;5;196m",
        "orange": "\033[38;5;214m",
        "yellow": "\033[38;5;226m",
        "green": "\033[38;5;40m",
        "cyan": "\033[38;5;51m",
        "teal": "\033[38;5;30m",
        "light blue": "\033[38;5;81m",
        "blue": "\033[38;5;21m",
        "purple": "\033[38;5;93m",
        "reset": "\033[0m"
    }

    # Command dictionary with all accepted commands
    commands = {
        "/join": "To join a private room use /join <room name>",
        "/leave": "To leave a private room and return to the public chat",
        "/exit": "To completely leave the server (disconnect from it)"
        # Can add more later if extra features are added
    }

    def __init__(self):
        self.clients = [] # Stores clients' sockets
        self.usernames = [] # Stores client usernames
        self.colors = [] # Stores client colors
        self.rooms = {'public': []} # Tracks which client is in which room
        self.client_rooms = {} # Tracks which room each client is in
        self.server = None # The server starts off with no listening socket
        self.lock = threading.Lock() # Threading lock just to be safe :)