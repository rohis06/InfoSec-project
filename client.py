import socket
import binascii
import time
import struct

# DNS Header

# Only working on ID, QR, Opcode, TC, RD, and QDCount (all other fields get value of 0)

# ID = 1010101000000000 -> 16 bit identifier assigned by the program that generates any query. Used by the requester to match up replies

# QR = 0 -> One bit field that specifies whether this message is a query (0), or a response (1)

# Opcode = 0000 -> Four bit field that specifies kind of query, this one is a standard query

# TC = 0 -> Specifies that this message was truncated due to length greater than that permitted on the transmission channel

# RD = 1 -> Recurion Desired - It directs the name server to pursue the query recursively.

# QDCount = 0000000000000001 -> an unsigned 16 bit integer specifying the number of entries in the question section.

dnsHeader = "AA0001000001000000000000"

def input_padding(s):
    return '0x' + s[2:].zfill(2)

def dnsURLParser(user_input):
    host = ""
    tld = ""
    index_start = 0

    # Parse out hostname
    for element in range(0, len(user_input)):
        if user_input[element] == ".":
            index_start = element
            break
        else:
            host = host + user_input[element]

    # Parse out TLD
    for element in range(index_start+1, len(user_input)):
        tld = tld + user_input[element]


    hex_host = binascii.hexlify(host.encode("utf-8"))
    hex_tld = binascii.hexlify(tld.encode("utf-8"))

    len_host = input_padding(str(hex(len(host))))
    len_tld = input_padding(str(hex(len(tld))))

    query = len_host[2:] + hex_host.decode("utf-8") + len_tld[2:] + hex_tld.decode("utf-8")
    query = query.upper()
    #print(query)

    return query

def parse_query(decoded_data):
    len_host = ""
    host = ""
    len_tld = ""
    tld = ""

    for element_len_host in range(24, 26):
        len_host = len_host + decoded_data[element_len_host]
    
    host_index_last = 26+(int(len_host)*2)
    for element_host in range(26, host_index_last):
        host = host + decoded_data[element_host]
    #print("host: ", host)
    for element_len_tld in range(host_index_last, host_index_last+2):
        len_tld = len_tld + decoded_data[element_len_tld]
    #print("len: ", int(len_tld))
    tld_index_last = host_index_last+2+(int(len_tld)*2)
    for element_tld in range(host_index_last+2, tld_index_last):
        tld = tld + decoded_data[element_tld]
    
    offset_comp = tld_index_last+2+4+4
    offset = offset_comp - 24

    queryAnalyzed = decoded_data[24:24+offset]

    temp_host_name_object = bytes.fromhex(host)
    temp_tld_object = bytes.fromhex(tld)

    true_host_name = temp_host_name_object.decode("ASCII")
    true_tld = temp_tld_object.decode("ASCII")

    domain_name = true_host_name + "." + true_tld
    #print("queryAnalyzed: ", queryAnalyzed)
    #print("Received request for: ", domain_name)
    return domain_name, offset, queryAnalyzed

def parse_answer(decoded_data, offset):
    # Jump to location in packet
    start_index = 24 + offset
    ttl = ""
    rdata = ""
    # Rip raw data
    for elementTTL in range(start_index+12, start_index+20):
        ttl = ttl + decoded_data[elementTTL]
    for elementRDATA in range(start_index+24, start_index+32):
        rdata = rdata + decoded_data[elementRDATA]
    
    #Conversions
    address = int(rdata, 16)
    true_ttl = int(ttl, 16)
    ip_address = socket.inet_ntoa(struct.pack(">L", address))
    
    return ip_address, true_ttl, time.time()

def main():
    HOST = "127.0.0.1"
    PORT = 8003

    # Create server socket
    response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # In case you want to kill and restart
    response_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the application
    response_socket.bind((HOST, PORT))

    url = input("Enter a domain name (e.g. youtube.com): ")
    query = dnsURLParser(url)
    dnsQuestion = query + "000001" + "0001"
    dnsQuery = dnsHeader + dnsQuestion
    
    # create client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    server_addr = ("127.0.0.1", 8002)

    # DNS queries for sites
    #test_dns_queryYT = "AA000100000100000000000007796F757475626503636F6D0000010001"
    #test_dns_queryFB = "AA00010000010000000000000866616365626F6F6B03636F6D0000010001"
    #test_dns_queryTMZ = "AA000100000100000000000003746D7A03636F6D0000010001"
    #test_dns_queryNYT = "AA0001000001000000000000076E7974696D657303636F6D0000010001"
    #test_dns_queryCNN = "AA000100000100000000000003636E6E03636F6D0000010001"

    # Change this last part here to whichever
    client_socket.sendto(dnsQuery.encode(), server_addr)
    requested_data, _ = response_socket.recvfrom(4096)
    decoded_data = binascii.hexlify(requested_data).decode("utf-8")
    requested_website, offset, queryAnalyzed = parse_query(decoded_data)
    ip_addr, ttl, time_received = parse_answer(decoded_data, offset)
    print("Received IP Address for " + url + ": " + ip_addr)

main()