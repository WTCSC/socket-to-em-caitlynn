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

    def make_dat_connection(self, username):
        self.username = username
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(10)
        logger.debug(f"Attempting a connection to {self.host}:{self.port}")
        self.client.connect((self.host, self.port))
        self.client.settimeout(None)

        self.client.send(username.encode('utf-8'))
        logger.info(f"Connected as the user {username}")

    def get_dat_message(self):
        try:
            while True:
                message = self.client.recv(1024).decode('utf-8')

                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.flush()

                print(message)

                sys.stdout.write(f"{self.username}: ")
                sys.stdout.flush()
        
        except:
            print("You disconnected from the server (~‾‾∇‾‾  )~ bye~")
            self.client.close()

    def send_dat_message(self):
        try:
            while True:
                sys.stdout.write(f"{self.username}: ")
                sys.stdout.flush()
                message = input()

                if message == "/exit":
                    self.client.send(message.encode('utf-8'))
                    print("You have left the chat (~‾‾∇‾‾  )~ bye~")
                    self.client.close()
                    sys.exit(0)

                else:
                    self.client.send(f"{message}".encode('utf-8'))
                    sys.stdout.write('\r' + ' ' * 80 + '\r')
                    sys.stdout.flush()

        except (KeyboardInterrupt, EOFError): 
            self.client.send("/exit".encode('utf-8'))
            self.client.close()
            print("You disconnected from the server (~‾‾∇‾‾  )~ bye~")
            sys.exit(0)

    def start_dat_client(self):
        receive_thread = threading.Thread(target=self.get_dat_message)
        receive_thread.start()

        send_thread = threading.Thread(target=self.send_dat_message)
        send_thread.start()

def main():
    client = Client()
    username = input("Enter your username:")
    client.make_dat_connection(username)
    client.start_dat_client()

if __name__ == "__main__":
    main()