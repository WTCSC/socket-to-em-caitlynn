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

    # Command dictionary with all accepted commands and descriptions
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

    # Sends, "broadcasts", a message to every user in the same room
    def broadcast_dat_message(self, message, senders_client):

            # Gets the sender's room which defaults to public
            senders_room = self.client_rooms.get(senders_client, 'public')

            # Log Dmessages sent at a debug level
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
                    except Exception as e:
                        # If it fails, remove the client and log the error
                        logger.error(f"An error occured when sending the message:{e}")
                        self.remove_dat_client(client)

    # Removes a client from the server and all internal tracking
    def remove_dat_client(self, client):
        with self.lock:
            # Locates the passed client in the index and username tracking
            if client in self.clients:
                index = self.clients.index(client)
                username = self.usernames[index]
                
                # Basically removes the client from the list of people in a room and informs everyone else about it
                room = self.client_rooms.get(client, 'public')
                if room in self.rooms and client in self.rooms[room]:
                    self.rooms[room].remove(client)
                    self.broadcast_dat_message(f"{username} has left the chat  (~‾‾∇‾‾  )~ bye~".encode('utf-8'), client)

                # Actually removes the client from the room itself
                if client in self.client_rooms:
                    del self.client_rooms[client]

                # Continues to remove the client from all other lists of tracking
                self.clients.remove(client)
                self.usernames.pop(index)
                self.colors.pop(index)

                # Logs that they left and prints it to the server terminal as well
                client.close()
                logger.info(f"{username} has disconnected  (~‾‾∇‾‾  )~ bye~")
                print(f"{username} has disconnected  (~‾‾∇‾‾  )~ bye~")

    # Handles and processes all of the passable commands
    def handle_dat_client(self, client):
        while True:
            try:
                # Takes the message from the client
                message = client.recv(1024).decode('utf-8')

                # Handles if the client wants to join a room using /join
                if message.startswith("/join "):
                    room_name = message.split(" ", 1)[1].strip()
                    self.join_dat_room(client, room_name)

                # Handles if the client wants to leave a room using /leave
                elif message == "/leave":
                    self.leave_dat_room(client)
                
                # Handles if the client wants to exit a room using /exit
                elif message == "/exit":
                    self.remove_dat_client(client)
                    break
                
                # This is just for regular message handling
                else:
                    username = self.usernames[self.clients.index(client)]
                    color = self.colors[self.clients.index(client)]
                    colored_message = f"{color}{username}: {message}{self.color_codes['reset']}"
                    self.broadcast_dat_message(colored_message.encode('utf-8'), client)

            # If it fails, remove the client and log the error
            except Exception as e:
                logger.error(f"An error occured when processing the message:{e}")
                self.remove_dat_client(client)
                break

    # Move a client into a room a/o makes it if it doesn't already exist
    def join_dat_room(self, client, room_name):
        with self.lock:
            # Gets the current room of the client
            current_room = self.client_rooms.get(client, 'public')

            # Removes the client from their current room
            if client in self.rooms[current_room]:
                self.rooms[current_room].remove(client)

            # Creates the room if it doesn't already exist
            if room_name not in self.rooms:
                self.rooms[room_name] = []

            # Adds the client to the room and updates the tracking interfaces
            self.rooms[room_name].append(client)
            self.client_rooms[client] = room_name

            # Communicates their joining to other users in the room
            username = self.usernames[self.clients.index(client)]
            self.broadcast_dat_message(f"{username} has joined the room {room_name} |˶˙ᵕ˙ )ﾉﾞ".encode('utf-8'), client)
            client.send(f"You joined the room {room_name} |˶˙ᵕ˙ )ﾉﾞBe sure to use /leave to leave the room".encode('utf-8'))

    # Moves a client back to the public room if they aren't there already
    def leave_dat_room(self, client):
        # Gets the current room of the client
        current_room = self.client_rooms.get(client, 'public')

        # Checks to make sure the client isn't in public
        if current_room != "public":
            
            # Removes the clients from their current room
            if client in self.rooms[current_room]:
                self.rooms[current_room].remove(client)

            # Communicates that they left to other users in the room
            username = self.usernames[self.clients.index(client)]
            self.broadcast_dat_message(f"{username} has left the room  (~‾‾∇‾‾  )~ bye~".encode('utf-8'), client)

            # Moves and updates the client's room in real time and within tracking interfacesf
            self.client_rooms[client] = "public"
            self.rooms['public'].append(client)
            client.send(f"You've returned to the public chat!".encode('utf-8'))

    # Handles the client choosing their color
    def choose_color(self, client):
        with self.lock:
            # Sends a messager to the client of the availble colors
            color_options = "\nAvailable colors: black, white, pink, red, orange, yellow, green, cyan, teal, light blue, blue, purple"
            client.send(f"Feel free to chose a color for your messages ₍^ >ヮ<^₎ .ᐟ.ᐟ {color_options}".encode('utf-8'))

            # Receieves the color inputed by the client. Lowers and strips it just to be sure
            color_choice = client.recv(1024).decode('utf-8').lower().strip() 

            # Logs the color received for debugging purposes
            logger.debug(f"Received color choice: '{color_choice}'")

            # If the color given exists in the availble options, changes the client's text color to it
            if color_choice in self.color_codes:
                index = self.clients.index(client)
                self.colors[index] = self.color_codes[color_choice]
                client.send(f"Your color has been set to {color_choice} ദ്ദി ( ᵔ ᗜ ᵔ )".encode('utf-8'))

            # Else, just sets it to white (default)
            else:
                index = self.clients.index(client)
                self.colors[index] = self.color_codes["white"]
                client.send("Since an invalid color choice was given, your color is white ദ്ദി ( ᵔ ᗜ ᵔ )".encode('utf-8'))

    # Starts the server :D
    def start_dat_server(self):
        # Starts the server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Binds and starts listening
        try:
            self.server.bind((self.host, self.port))
            self.server.listen(5) # Allows five connections at once
            self.server.settimeout(1) # One second time out
            logger.success(f"Server running on {self.host}:{self.port}")

            while True:
                try:
                    # Accepts new connections
                    client, address = self.server.accept()
                    logger.info(f"There's a new connection from {address}₍^ >ヮ<^₎ .ᐟ.ᐟ")
                    print(f"There's a new connection from {address}₍^ >ヮ<^₎ .ᐟ.ᐟ")

                    # Gets and stores new user info within tracking interfaces
                    username = client.recv(1024).decode('utf-8')
                    self.usernames.append(username)
                    self.clients.append(client)
                    self.colors.append(self.color_codes['white'])

                    # Adds the client to the public room by default
                    self.rooms['public'].append(client)
                    self.client_rooms[client] = "public"

                    # Logs and communicates the connection to other clients in the room
                    logger.debug(f"Username of the client: {username}")
                    print(f"{username} has joined the server ₍^ >ヮ<^₎ .ᐟ.ᐟ")
                    self.broadcast_dat_message(f"{username} has joined the public chat ₍^ >ヮ<^₎ .ᐟ.ᐟ".encode('utf-8'), client)

                    # Allows the user to choose their color
                    self.choose_color(client)

                    # Tells the client that they've conneted to the server and gives them the basic set of commands
                    client.send("You are now connected to the server ₍^ >ヮ<^₎ .ᐟ.ᐟ \nHere are some commands:\n join <room> (to join a room)\n/leave (to leave a room)\n/exit (to leave the server)".encode('utf-8'))

                    # Starts a thread for the client
                    thread = threading.Thread(target=self.handle_dat_client, args=(client,))
                    thread.start()

                # If it times out, then just keep the loop going
                except socket.timeout:
                    pass

        # Shuts the server down with a control C and logs it as well
        except KeyboardInterrupt:
            logger.warning("The server is shutting down ૮(˶ㅠ︿ㅠ)ა")
            self.server.close()
            sys.exit(0)

# Executes main and makes the whole thing run
def main():
    server = Server()
    server.start_dat_server()

if __name__ == "__main__":
    main()