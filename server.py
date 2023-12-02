import socket
import binascii
import time
import struct

# For ease of understanding, outputs will be printed within the terminal
# This server is running @ 127.0.0.1 on Port 8002

# Define some helper functions

# Requests from UC Davis DNS server
def request(dnsQuery):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = ("169.237.229.88", 53)
    client_socket.sendto(binascii.unhexlify(dnsQuery), server_addr)
    dns_requested_data, _ = client_socket.recvfrom(4096)
    decoded_dns_data = binascii.hexlify(dns_requested_data).decode("utf-8")
    return decoded_dns_data


def response(transactionID, queryInput, ip_address):
    # Build up DNS response
    appendedIP = binascii.hexlify(socket.inet_aton(ip_address)).decode("utf-8")
    #print(appendedIP)
    id = transactionID
    flags = "8000"
    qdCount = "0001"
    answerRR = "0001"
    authorityRR = "0000"
    additionalRR = "0000"
    query = queryInput
    answer = "c00c000100010000003c0004" + appendedIP

    dnsResponse = id + flags + qdCount + answerRR + authorityRR + additionalRR + query + answer
    response_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Assuming client is listening at port 8003, send response there
    client_addr = ("127.0.0.1", 8003)
    response_socket.sendto(binascii.unhexlify(dnsResponse), client_addr)
    

def parse_header(decoded_data):
    id = ""
    flags = ""
    questions = ""
    answer_rr = ""
    authority_rr = ""
    additional_rr = ""


    for elementID in range(0, 4):
        id = id + decoded_data[elementID]
    
    for elementFlags in range(4, 8):
        flags = flags + decoded_data[elementFlags]

    for elementQuestions in range(8, 12):
        questions = questions + decoded_data[elementQuestions]
    
    for elementAnswerRR in range(12, 16):
        answer_rr = answer_rr + decoded_data[elementAnswerRR]
    
    for elementAuthorityRR in range(16, 20):
        authority_rr = authority_rr + decoded_data[elementAuthorityRR]
    
    for elementAdditionalRR in range(20, 24):
        additional_rr = additional_rr + decoded_data[elementAdditionalRR]
    
    #print("ID: ", bin(int(id, 16))[2:].zfill(16))
    #print("Flags: ", bin(int(flags, 16))[2:].zfill(16))
    #print("Number of entries in question section: ", int(questions, 16))
    #print("Number of resource records in the answer section: ", int(answer_rr, 16))
    #print("Number of name server resource records in the authority records section: ", int(authority_rr, 16))
    #print("Number of resource records in the additional records section: ", int(additional_rr, 16))

    return int(questions, 16), id

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

    

# Now begin actual server
# Run on local machine
HOST = "127.0.0.1"
PORT = 8002

# Create server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# In case you want to kill and restart
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind the application
server_socket.bind((HOST, PORT))

cache = {}

# This part opens a port, then parses the request
# If the IP address for a domain does not exist, the server will retrieve it
# Else the server will return the cached data it has
    # If the cached data is expired, then the DNS server will retrieve a new copy

while True:
    data, addr = server_socket.recvfrom(4096)
    start_time = time.time()
    decoded_data = str(data.decode("utf-8"))
    num_questions, transactionID = parse_header(decoded_data)
    requested_website, offset, queryAnalyzed = parse_query(decoded_data)

    return_val = cache.get(requested_website)
    if return_val == None:
        #print("It's not here!")
        dns_decoded_data = request(decoded_data)
        ip_addr, ttl, time_received = parse_answer(dns_decoded_data, offset)
        
        # Create entry
        cache[requested_website] = {"IP": ip_addr, "TTL": ttl, "Time": time_received}
        print("")
        print("Created new entry in cache for " + requested_website + " with IP address: " + cache[requested_website]["IP"])
        response(transactionID, queryAnalyzed, ip_addr)

    else:
        # Check if TTL expired
        lifetime = time.time() - cache[requested_website]["Time"]
        print("")
        print("Website: ", requested_website)
        print("Current lifetime: ", lifetime)
        print("TTL in cache: ", cache[requested_website]["TTL"])
        # Not expired
        if (lifetime < cache[requested_website]["TTL"]):
            #print("It's here!")
            print("RTT: " + str(time.time()-start_time))
            print("Cached IP Address for " + requested_website + ": " + cache[requested_website]["IP"])
            response(transactionID, queryAnalyzed, ip_addr)
        
        # Expired
        else:
            #print("Expired")
            dns_decoded_data = request(decoded_data)
            ip_addr, ttl, time_received = parse_answer(dns_decoded_data, offset)
            
            # Create new entry
            cache[requested_website] = {"IP": ip_addr, "TTL": ttl, "Time": time_received}
            print("Previously cached IP address expired for " + requested_website + " here's a new one: " + cache[requested_website]["IP"])
            response(transactionID, queryAnalyzed, ip_addr)
            #print(cache[requested_website]["IP"])
            #print(cache[requested_website]["TTL"])