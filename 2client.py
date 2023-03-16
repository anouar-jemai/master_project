import socket
import ssl

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# wrap the socket in SSL
ssl_sock = ssl.wrap_socket(s,
                           cert_reqs=ssl.CERT_NONE,
                           ssl_version=ssl.PROTOCOL_TLSv1_2)

# connect to the socksv5 proxy server
ssl_sock.connect(('localhost', 8888))

# send the SOCKSv5 authentication and connection request to the proxy server
ssl_sock.send(b'\x05\x01\x00')

# receive the SOCKSv5 server response from the proxy server
response = ssl_sock.recv(1024)

# check if the SOCKSv5 server response is valid
if response[:2] == b'\x05\x00':
    # send the data to the server through the SOCKSv5 proxy
    ssl_sock.send(b'Hello, server!')

    # receive the data from the server through the SOCKSv5 proxy
    data = ssl_sock.recv(1024)
    print("Received from server: %s" % data.decode())

# close the SSL socket
ssl_sock.close()
