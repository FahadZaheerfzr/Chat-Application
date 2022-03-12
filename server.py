import socket
from threading import Thread

# server's IP address
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 3001  # port we want to use

separator_token = "<SEP>"  # we will use this to separate the client name & message

# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

usernameMap = {}

def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")

            # Also remove client socket from username mapping 
            # it can no longer be reached
            for key,val in usernameMap.items():
                if val == cs:
                    del usernameMap[key]
            client_sockets.remove(cs)
        else:
            # if we received a message, replace the <SEP>
            # token with ": " for nice printing
            if separator_token in msg:
                msg = msg.replace(separator_token, ": ")
            else:
                # Mapping the username to sockets for private chat
                usernameMap[msg] = cs
                continue
        
        # If it is a private message
        if msg.startswith("<<"):
            # formatting for removing unnecessary text
            msg = msg[2:]
            # separating username and message
            parts = msg.split(">>")

            # Find the socket for that username
            try:
                privateClientSocket = usernameMap[parts[0]]
                # Add private label to the message
                msgSend = "<Private> " + parts[1]
                # send that user the message
                privateClientSocket.send(msgSend.encode())
            except:
                # Let sender no that no such user in chat
                errorMsg = "No such user in chat"
                cs.send(errorMsg.encode())
            continue
            
        # Broadcast message
        for client_socket in client_sockets:
            # and send the message
            client_socket.send(msg.encode())


while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    # add the new connected client to connected sockets
    client_sockets.add(client_socket)
    # start a new thread that listens for each client's messages
    t = Thread(target=listen_for_client, args=(client_socket,))
    # make the thread daemon so it ends whenever the main thread ends
    t.daemon = True
    # start the thread
    t.start()

# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()