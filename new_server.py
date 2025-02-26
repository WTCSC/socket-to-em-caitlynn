import socket
import sys
import threading
from loguru import logger

# Configuring Loguru for clean loggin
logger.remove()

# Writes anything that is log level WARNING or higher to the terminal (can be changed)
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="WARNING",
    colorize=True
) 

# Writes all debug and higher logs to a log file (capped at 500KB and only kept for a week)
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

    def broadcast(self, message, senders_client):
        
            senders_room = self.client_rooms.get(senders_client, 'public')

            logger.debug(f"Sender's room: {senders_room}")
            logger.debug(f"All rooms: {self.rooms}")
            logger.debug(f"Client room mappings: {self.client_rooms}")

            # Finds everyone in the same room as the sender
            viewers = self.rooms.get(senders_room,[])

            # This will send a message to everyone in the same room as the sender- minus the sender of course
            for client in viewers:
                if client != senders_client:
                    try:
                        client.send(message)
                    except:
                        self.remove_client(client)

    def remove_client(self, client):
        
        # Might also need to remove this lock later :D
        with self.lock:
            if client in self.clients:
                index = self.clients.index(client)
                username = self.usernames[index]
                
                room = self.client_rooms.get(client, 'public')
                if room in self.rooms and client in self.rooms[room]:
                    self.rooms[room].remove(client)
                    self.broadcast(f"{username} has left the chat  (~‾‾∇‾‾  )~ bye~".encode('utf-8'), client)

                if client in self.client_rooms:
                    del self.client_rooms[client]

                self.clients.remove(client)
                self.usernames.pop(index)
                self.colors.pop(index)

                client.close()
                logger.info(f"{username} has disconnected  (~‾‾∇‾‾  )~ bye~")
                print(f"{username} has disconnected  (~‾‾∇‾‾  )~ bye~")

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')

            # Handles if the client wants to join a room using /join
                if message.startswith("/join "):
                    room_name = message.split(" ", 1)[1].strip()
                    self.join_room(client, room_name)

                # Handles if the client wants to leave a room using /leave
                elif message == "/leave":
                    self.leave_room(client)
                
                # Handles if the client wants to exit a room using /exit
                elif message == "/exit":
                    self.remove_client(client)
                    break

                else:
                    username = self.usernames[self.clients.index(client)]
                    color = self.colors[self.clients.index(client)]
                    colored_message = f"{color}{username}: {message}{self.color_codes['reset']}"
                    self.broadcast(colored_message.encode('utf-8'), client)

            except:
                self.remove_client(client)
                break

    def join_room(self, client, room_name):
        with self.lock:
            current_room = self.client_rooms.get(client, 'public')

            # Removes the client from their current room
            if client in self.rooms[current_room]:
                self.rooms[current_room].remove(client)

            if room_name not in self.rooms:
                self.rooms[room_name] = []

            self.rooms[room_name].append(client)
            self.client_rooms[client] = room_name

            username = self.usernames[self.clients.index(client)]
            self.broadcast(f"{username} has joined the room {room_name} |˶˙ᵕ˙ )ﾉﾞ".encode('utf-8'), client)
            client.send(f"You joined the room {room_name} |˶˙ᵕ˙ )ﾉﾞBe sure to use /leave to leave the room".encode('utf-8'))

    def leave_room(self, client):
        room = self.client_rooms.get(client, 'public')

        if room != "public":
                
            if client in self.rooms[room]:
                self.rooms[room].remove(client)

            username = self.usernames[self.clients.index(client)]
            self.broadcast(f"{username} has left the room  (~‾‾∇‾‾  )~ bye~".encode('utf-8'), client)

            self.client_rooms[client] = "public"
            self.rooms['public'].append(client)
            client.send(f"You've returned to the public chat!".encode('utf-8'))

    def choose_color(self, client):
        with self.lock:
            color_options = "\nAvailable colors: black, white, pink, red, orange, yellow, green, cyan, teal, light blue, blue, purple"
            client.send(f"Feel free to chose a color for your messages ₍^ >ヮ<^₎ .ᐟ.ᐟ {color_options}".encode('utf-8'))

            color_choice = client.recv(1024).decode('utf-8').lower().strip() 

            logger.debug(f"Received color choice: '{color_choice}'")

            if color_choice in self.color_codes:
                index = self.clients.index(client)
                self.colors[index] = self.color_codes[color_choice]
                client.send(f"Your color has been set to {color_choice} ദ്ദി ( ᵔ ᗜ ᵔ )".encode('utf-8'))

            else:
                index = self.clients.index(client)
                self.colors[index] = self.color_codes["white"]
                client.send("Since an invalid color choice was given, your color is white ദ്ദി ( ᵔ ᗜ ᵔ )".encode('utf-8'))

    def start_dat_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.server.settimeout(1)
            logger.success(f"Server running on {self.host}:{self.port}")

            while True:
                try:
                    client, address = self.server.accept()
                    logger.info(f"There's a new connection from {address}₍^ >ヮ<^₎ .ᐟ.ᐟ")
                    print(f"There's a new connection from {address}₍^ >ヮ<^₎ .ᐟ.ᐟ")

                    username = client.recv(1024).decode('utf-8')
                    self.usernames.append(username)
                    self.clients.append(client)
                    self.colors.append(self.color_codes['white'])

                    self.rooms['public'].append(client)
                    self.client_rooms[client] = "public"

                    logger.debug(f"Username of the client: {username}")
                    print(f"{username} has joined the server ₍^ >ヮ<^₎ .ᐟ.ᐟ")
                    self.broadcast(f"{username} has joined the public chat ₍^ >ヮ<^₎ .ᐟ.ᐟ".encode('utf-8'), client)

                    self.choose_color(client)

                    client.send("You are now connected to the server ₍^ >ヮ<^₎ .ᐟ.ᐟ \nHere are some commands:\n join <room> (to join a room)\n/leave (to leave a room)\n/exit (to leave the server)".encode('utf-8'))

                    thread = threading.Thread(target=self.handle_client, args=(client,))
                    thread.start()

                except socket.timeout:
                    pass

        except KeyboardInterrupt:
            logger.warning("The server is shutting down ૮(˶ㅠ︿ㅠ)ა")
            self.server.close()
            sys.exit(0)

def main():
    server = Server()
    server.start_dat_server()

if __name__ == "__main__":
    main()