import socket

# create client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_addr = ("127.0.0.1", 8002)

# DNS queries for sites
test_dns_queryYT = "AA000100000100000000000007796F757475626503636F6D0000010001"
test_dns_queryFB = "AA00010000010000000000000866616365626F6F6B03636F6D0000010001"
test_dns_queryTMZ = "AA000100000100000000000003746D7A03636F6D0000010001"
test_dns_queryNYT = "AA0001000001000000000000076E7974696D657303636F6D0000010001"
test_dns_queryCNN = "AA000100000100000000000003636E6E03636F6D0000010001"

# Change this last part here to whichever
client_socket.sendto(test_dns_queryCNN.encode(), server_addr)