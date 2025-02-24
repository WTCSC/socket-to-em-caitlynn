import socket
import sys
import threading

# Some server settings
Host = '127.0.0.1'
Port = 1270

username = input("Enter your username:")

# Establish the server connection
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((Host, Port))
client.send(username.encode('utf-8'))

def get_that_message():
    try:
        while True:
            message = client.recv(1024).decode('utf-8')

            sys.stdout.write('\r' + ' ' * 80 + '\r')
            sys.stdout.flush()

            print(message)

            sys.stdout.write(f"{username}: ")
            sys.stdout.flush()
    
    except:
        print("You disconnected from the server (~‾‾∇‾‾  )~ bye~")
        client.close()

def send_that_message():
    try:
        while True:
            sys.stdout.write(f"{username}: ")
            sys.stdout.flush()
            message = input()

            if message == "/exit":
                client.send(message.encode('utf-8'))
                print("You have left the chat (~‾‾∇‾‾  )~ bye~")
                client.close()
                sys.exit(0)

            else:
                client.send(f"{message}".encode('utf-8'))
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.flush()

    except (KeyboardInterrupt, EOFError): 
        client.send("/exit".encode('utf-8'))
        client.close()
        print("You disconnected from the server (~‾‾∇‾‾  )~ bye~")
        sys.exit(0)

receive_thread = threading.Thread(target=get_that_message)
receive_thread.start()

send_thread = threading.Thread(target=send_that_message)
send_thread.start()