# Python 3.6 NOTE: We will use importlib to find if netaddr is installed. If not, we quit.
import importlib
import sys # Python 3.6 NOTE: We need this for the getsizeof method to replace "sizeof" in Py 2 code
if sys.hexversion < 50725360:
    print("ERROR: Please utilize following 3.6.1 version of Python:\r\n\r\n >>>sys.hexversion\r\n50725360\r\n\r\n")
    sys.exit(0)
if importlib.find_loader('netaddr') is None:
    print("ERROR: netaddr is not installed; please run: \r\n\r\n    easy_install netaddr\r\n\r\nQuiting...\r\n")
    sys.exit(0)
from netaddr import IPNetwork,IPAddress 
import socket
import os
import struct
import time
import threading
from ctypes import *
# host to listen on
host = "0.0.0.0" # TODO: User needs to replace host IP and subnet below

# subnet to target
subnet = "192.168.200.0/24" # TODO: User needs to replace this

# magic string we'll check ICMP responses for
magic_message = "PYTHONRULES!"

# this sprays out the UDP datagrams
def udp_sender(subnet,magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    for ip in IPNetwork(subnet):
        try: # Python 3.6 NOTE: str.encode is applied for bytes conversion
            sender.sendto(str.encode(magic_message),("%s" % ip,65212))
        except:
            pass
    
# our IP header
class IP(Structure):
    _fields_ = [
            ("ihl",          c_ubyte, 4),
            ("version",      c_ubyte, 4),
            ("tos",          c_ubyte),
            ("len",          c_ushort),
            ("id",           c_ushort),
            ("offset",       c_ushort),
            ("ttl",          c_ubyte),
            ("protocol_num", c_ubyte),
            ("sum",          c_ushort),
            ("src",          c_ulong),
            ("dst",          c_ulong),
            ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        # map protocol constants to their names
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}

        # human readable IP addresses
        self.src_address = socket.inet_ntoa(struct.pack("<L",self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L",self.dst))

        # human readable protocol
        try: 
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMP(Structure):

    _fields_ = [
            ("type",         c_ubyte),
            ("code",         c_ubyte),
            ("checksum",     c_ushort),
            ("unused",       c_ushort),
            ("next_hop_mtu", c_ushort)
            ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass

# this should look familiar from the previous example
if os.name == "nt":
    socket_protocol = socket.IPPROTO_IP
else: 
    socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

    sniffer.bind((host, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# start sending packets
t = threading.Thread(target=udp_sender,args=(subnet,magic_message))
t.start()

try:

    while True:
        # read in a packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # create an IP header from the first 32(!) bytes of the buffer
        ip_header = IP(raw_buffer[0:32]) # Python 3.6 NOTE: 20-bytes might break < Python 3.6

        # print out the protocol that was detected and the hosts 
        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address)) # Python 3.6 NOTE: Print statement replacement per Python 3. 

        # if it's ICMP, we want it
        if ip_header.protocol == "ICMP":

            # calculate where our ICMP packet starts # Py 3.6 NOTE: sys.getsizeof method used for buf 
            offset = ip_header.ihl * 4
            buf = raw_buffer[offset:offset + sys.getsizeof(ICMP)] 
            
            # create our ICMP structure
            icmp_header = ICMP(buf)

            print("ICMP -> Type: %d Code: %d" % (icmp_header.type, icmp_header.code))

            # now check for the TYPE 3 and CODE
            if icmp_header.code == 3 and icmp_header.type == 3:

                # make sure host is in our target subnet
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):

                    # make sure it has our magic message # Python 3.6 NOTE: and apply bytes type here too
                    if raw_buffer[len(raw_buffer)-len(str.encode(magic_message)):] == str.encode(magic_message):
                        print("Host Up: %s" % ip_header.src_address)
                
# handle CTRL - C
except KeyboardInterrupt: 
    
    # if we're using Windows turn off promiscuous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF) 
