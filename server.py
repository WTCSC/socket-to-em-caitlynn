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
    "purple": "\033[38;5;93m",
    "reset": "\033[0m"
}

# "Broadcasts" aka sends a message to the sender's room
def broadcast(message, senders_client):
    # Gets the sender's current room
    senders_room = client_rooms.get(senders_client, 'public')

    print(f"Sender's room: {senders_room}")
    print(f"All rooms: {rooms}")
    print(f"Client room mappings: {client_rooms}")

    viewers = []

    # Finds everyone in the same room as the sender
    if senders_room in rooms:
        viewers = rooms[senders_room]
    
    # This will send a message to everyone in the same room as the sender- minus the sender of course
    for client in viewers:
        if client != senders_client:
            try:
                client.send(message)
            except:
                remove_client(client)

# Should a user choose to leave this will remove them from their current room, as well as all structures
def remove_client(client):
    for client in clients:
        index = clients.index(client)
        username = usernames.index
        clients.remove(client)
        usernames.pop(index)
        colors.pop(index)
        
        room = client_rooms.get(client, 'public')
        if room in rooms and client in rooms[room]:
            rooms[room].remove(client)
            broadcast(f"{username} has left the chat  (~‾‾∇‾‾  )~ bye~".encode('utf-8'), client)

        del client_rooms[client]
        client.close
        print(f"{username} has disconnected  (~‾‾∇‾‾  )~ bye~")

# Handles the three passable commands from the user
def handle_client(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')

        # Handels if the client wants to join a room using /join
            if message.startswith("/join "):
                room_name = message.split(" ", 1)[1].strip()
                join_room(client, room_name)

            # Handels if the client wants to leave a room using /leave
            elif message == "/leave":
                leave_room(client)
            
            # Handels if the client wants to exit a room using /exit
            elif message == "/exit":
                remove_client(client)
                break

            else:
                username = usernames[clients.index(client)]
                color = colors[client.index(client)]
                colored_message = f"{color}{username}: {message}{color_codes['reset']}"
                broadcast(colored_message.encode('utf-8'), client)

        except:
            remove_client(client)
            break

# Should a user want to join a room, this will communicate this to the user and the other users
def join_room(client, room_name):
    current_room = client_rooms.get(client, 'public')

    # Removes the client from their current room
    if client in rooms[current_room]:
        rooms[current_room].remove(client)

    if room_name not in rooms:
        rooms[room_name] = []

    rooms[room_name].append(client)
    client_rooms[client] = room_name

    username = usernames.index[clients.index(client)]
    broadcast(f"{username} has joined the room {room_name} |˶˙ᵕ˙ )ﾉﾞ".encode('utf-8'), client)
    client.send(f"You joined the room {room_name} |˶˙ᵕ˙ )ﾉﾞ".encode('utf-8'))

# Should a user want to leave a room, this will communicate this to the user and the other users
def leave_room(client):
    room = client_rooms.get(client, 'public')

    if room != "public":
        
        if client in rooms[room]:
            rooms[room].remove(client)
        
        username = usernames[clients.index(client)]
        broadcast(f"{username} has left the room  (~‾‾∇‾‾  )~ bye~".encode('utf-8'), client)
        
        client_rooms[client] = "public"
        rooms['public'].append(client)
        client.send(f"You've returned to the public chat!".encode('utf-8'), client)

# Allows the user to choose the color that they will show in the chat room
def choose_color(client):
    color_options = "\nAvailable colors: black, white, pink, red, orange, yellow, green, cyan, light blue, blue, purple"
    client.send(f"Feel free to chose a color for your messages ₍^ >ヮ<^₎ .ᐟ.ᐟ {color_options}".encode('utf-8'))

    color_choice = client.recv(1024).decode('utf-8').lower()
    if color_choice not in color_codes:
        color_choice = "white"
        client.send("White was chosen since an invalid color choice was provided ദ്ദി ( ᵔ ᗜ ᵔ )".encode('utc-8'))

    index = clients.index(client)
    colors[index] = color_codes[color_choice]

# Actually starts the chatroom server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((Host, Port))
    server.listen()

    print(f"Now listening on {Host} : {Port}")

    try:
        while True:
            client, address = server.accept()
            print(f"There's a new connection from {address}₍^ >ヮ<^₎ .ᐟ.ᐟ")

            client.send('Username'.encode('utf-8'))
            username = client.recv(1024).decode('utf.8')
            usernames.append(username)
            clients.append(client)
            colors.append(color_codes['white'])

            rooms['public'].append(client)
            client_rooms[client] = "public"

            print(f"Username of the client: {username}")
            broadcast(f"{username} has joined the public chat ₍^ >ヮ<^₎ .ᐟ.ᐟ".encode('utf-8'), client)

            choose_color(client)

            client.send("You are now connected to the server ₍^ >ヮ<^₎ .ᐟ.ᐟ \nHere are some commands:\n join <room> \n/leave \n/exit")

            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()

    except KeyboardInterrupt:
        print("\nThe server is shutting down ૮(˶ㅠ︿ㅠ)ა")
        server.close
        sys.exit(0)

# To actually run the server
start_server()