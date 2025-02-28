import socket
import sys
import threading
from loguru import logger

# Configuring Loguru for clean loggin
logger.remove()

# Writes anything that is log level WARNING or higher to the terminal (can be changed)
logger.add(
    sys.stderr,
    # Sets standard formatting for all logs
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="WARNING",
    colorize=True
) 

# Writes all debug and higher logs to a log file (capped at 500KB and only kept for a week)
logger.add("client.log", rotation="500 KB", retention="7 Days", level="DEBUG") 

class Client:

    def __init__(self, host='127.0.0.1', port=1270):
        self.username = None
        self.host = host
        self.port = port

    # Connects the client to the server
    def make_dat_connection(self, username):
        # Gets the username of the client
        self.username = username
        
        # Creates the socket and connects it
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(10) # Sets a timeout
        logger.debug(f"Attempting a connection to {self.host}:{self.port}")
        self.client.connect((self.host, self.port))
        self.client.settimeout(None) # Resets the timeout if it does connect

        # Sends the username over the server for server use
        self.client.send(username.encode('utf-8'))
        logger.info(f"Connected as the user {username}")

    # A threading function that receives and displays the messages to the client
    def get_dat_message(self):
        try:
            while True:
                # Gets the message from the server
                message = self.client.recv(1024).decode('utf-8')

                # Clears the terminal line before...
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.flush()

                # ...printing the message to the terminal
                print(message)

                # Basially puts back the "<username>: " part of a message
                sys.stdout.write(f"{self.username}: ")
                sys.stdout.flush()
        
        except:
            # If connection/interuption error occurs then communicate this to the client
            print("You disconnected from the server (~‾‾∇‾‾  )~ bye~")
            self.client.close()

    # A threading fucntion that sends the client's message to the server
    def send_dat_message(self):
        try:
            while True:
                # Puts the "<username>: " part in front of the message given by the client
                sys.stdout.write(f"{self.username}: ")
                sys.stdout.flush()
                message = input()

                # Handles if the user wants to exit the server
                if message == "/exit":
                    self.client.send(message.encode('utf-8'))
                    print("You have left the chat (~‾‾∇‾‾  )~ bye~")
                    self.client.close()
                    sys.exit(0)

                # If it's not the exit command then it will just send the message as is
                else:
                    self.client.send(f"{message}".encode('utf-8'))
                    sys.stdout.write('\r' + ' ' * 80 + '\r')
                    sys.stdout.flush()

        # Handles any possible errors that can occur while sending a message and communicates that
        except (KeyboardInterrupt, EOFError): 
            self.client.send("/exit".encode('utf-8'))
            self.client.close()
            print("You disconnected from the server (~‾‾∇‾‾  )~ bye~")
            sys.exit(0)

    # Starts two threads at once for both receiving and sending messages
    def start_dat_client(self):
        # Thread for receiving messages
        receive_thread = threading.Thread(target=self.get_dat_message)
        receive_thread.start()

        # Thread for sending messages
        send_thread = threading.Thread(target=self.send_dat_message)
        send_thread.start()

# Makes the client and connects to the server
def main():
    client = Client()
    username = input("Enter your username:")
    client.make_dat_connection(username)
    client.start_dat_client()

if __name__ == "__main__":
    main()