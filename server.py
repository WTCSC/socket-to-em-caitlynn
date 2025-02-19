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
    senders_room = client_rooms.get(senders_client, 'public')

    if senders_room == 'public':
        for client in rooms['public']:
            if client != senders_client:
                try:
                    client.send(message)
                except:
                    remove_client(client)
    
    elif senders_room in rooms:
        for client in rooms[senders_room]:
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

    if current_room != "public":
        leave_room(client)

    if room_name not in rooms:
        rooms[room_name] = []

    rooms[room_name].append(client)
    client_rooms[client] = room_name

    username = usernames.index[clients.index(client)]
    broadcast(f"{username} has joined the room {room_name} |˶˙ᵕ˙ )ﾉﾞ".encode('utf-8'), client)
    client.send(f"You joined the room {room_name} |˶˙ᵕ˙ )ﾉﾞ".encode('utf-8'))

# Should a user want to leave a room, this will communicate this to the user and the other users
def leave_room(client):
    print()

# Allows the user to choose the color that they will show in the chat room
def choose_color(client):
    print()

# Actually starts the chatroom server
def start_server():
    print()