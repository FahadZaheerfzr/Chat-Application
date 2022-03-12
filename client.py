import imp
from re import I
import socket
import random
from threading import Thread
from datetime import datetime
from colorama import Fore, init, Back
from simple_term_menu import TerminalMenu


# init colors
init()

# set the available colors
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTWHITE_EX,
          Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
          ]

# choose a random color for the client
client_color = random.choice(colors)

# server's IP address
# if the server is not on this machine,
# put the private (network) IP address (e.g 192.168.1.2)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 3001  # server's port
separator_token = "<SEP>"  # we will use this to separate the client name & message

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")


# prompt the client for a name
name = input("Enter your name: ")

to_send = f"{name}"
# finally, send the message
s.send(to_send.encode())

def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        print("\n" + message)


# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

while True:
    # input message we want to send to the server
    terminal_menu = TerminalMenu(["Broadcast", "Private"])
    choice_index = terminal_menu.show()
    to_send = input("Enter your message: ")
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if choice_index == 1:
        clientSend = input("Enter username of the client: ")
        # add the datetime, name & the color of the sender
        to_send = f"<<{clientSend}>>{client_color}[{date_now}] {name}{separator_token}{to_send}{Fore.RESET}"
    else:
        # add the datetime, name & the color of the sender
        to_send = f"{client_color}[{date_now}] {name}{separator_token}{to_send}{Fore.RESET}"
    
    # finally, send the message
    s.send(to_send.encode())

# close the socket
s.close()