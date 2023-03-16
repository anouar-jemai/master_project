import socket
import ssl

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a public host and a port
serversocket.bind(('localhost', 8000))

# become a server socket
serversocket.listen(1)

while True:
    # accept connections from outside
    (clientsocket, address) = serversocket.accept()

    # wrap the clientsocket in SSL
    ssl_sock = ssl.wrap_socket(clientsocket,
                               server_side=True,
                               certfile="server.crt",
                               keyfile="server.key",
                               ssl_version=ssl.PROTOCOL_TLSv1_2)

    # receive data from the client through the SSL socket
    data = ssl_sock.recv(1024)
    print("Received from client: %s" % data.decode())

    # send data back to the client through the SSL socket
    ssl_sock.send("Hello, client!".encode())

    # close the SSL socket
    ssl_sock.close()
