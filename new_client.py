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

class Client:
    
    # Some server settings
    Host = '127.0.0.1'
    Port = 1270