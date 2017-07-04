import sys
import socket
import threading

# This is a listening server example that will simply regurgitate any TCP traffic on designated ports. 

bind_ip   = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Python 3.6 NOTE: This part added to allow more flexibility and user input with listener assignments
if len(sys.argv[1:]) < 1: 
    print("Usage: python proxy.py [local host IP address] [port number])\r\n")
    print("Because no are defined, will use default IP '0.0.0.0' and port '9999'")
elif len(sys.argv[1:]) == 1:
    print("Will use default port 9999.")
    bind_ip   = sys.argv[1]
else:    
    bind_ip   = sys.argv[1]
    bind_port = int(sys.argv[2])
    
server.bind((bind_ip,bind_port))

server.listen(5)

print("\r\n[*] Listening on %s:%d" % (bind_ip,bind_port)) #Python 3.6 NOTE: All prints converted to "()"

# this is our client-handling thread:
def handle_client(client_socket):

    # print out what the client sends
    request = client_socket.recv(1024)

    print("[*] Received: %s" % str(request,"utf+8")) # Python 3.6 NOTE: convert bytes rec. to string. 

    # send back a packet
    client_socket.send(str.encode("ACK!")) # Python 3.6 NOTE: Convert ACK to bytes.
    # print(client_socket.getpeername()) #NOTE: Redundant; covered in lines 29, 31.
    client_socket.close()

while True:
    client,addr = server.accept()

    print("[*] Accepted connection from: %s:%d" % (addr[0],addr[1]))

    # spin up our client thread to handle incoming data
    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start() 
