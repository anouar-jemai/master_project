import socket
import ssl
import threading

def handle_client(client_socket):
    # Receive the initial request from the client
    initial_request = client_socket.recv(1024)

    # Check if the request is a valid SocksV5 request
    if initial_request[:2] != b'\x05\x01':
        return

    # Extract the requested destination address and port
    address_type = initial_request[3]
    if address_type == 1:
        # IPv4 address
        dest_address = socket.inet_ntoa(initial_request[4:8])
        dest_port = int.from_bytes(initial_request[8:10], byteorder='big')
    elif address_type == 3:
        # Domain name
        dest_address_length = initial_request[4]
        dest_address = initial_request[5:5+dest_address_length].decode('utf-8')
        dest_port = int.from_bytes(initial_request[5+dest_address_length:7+dest_address_length], byteorder='big')
    elif address_type == 4:
        # IPv6 address
        dest_address = socket.inet_ntop(socket.AF_INET6, initial_request[4:20])
        dest_port = int.from_bytes(initial_request[20:22], byteorder='big')
    else:
        # Unsupported address type
        return

    # Connect to the destination server
    dest_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest_socket.connect((dest_address, dest_port))

    # Send a success response to the client
    response = b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + b'\x00\x00'
    client_socket.sendall(response)

    # Wrap the socket connections in a TLS encryption layer
    client_socket = ssl.wrap_socket(client_socket, server_side=True, certfile='server.crt', keyfile='server.key')
    dest_socket = ssl.wrap_socket(dest_socket, cert_reqs=ssl.CERT_REQUIRED, ca_certs='ca.crt')

    # Relay data between the client and destination server
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        dest_socket.sendall(data)
        response = dest_socket.recv(4096)
        if not response:
            break
        client_socket.sendall(response)

    # Close the connections
    dest_socket.close()
    client_socket.close()

def run_server(host, port):
    # Create a socket and bind to the specified host and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    while True:
        # Accept incoming connections
        client_socket, client_address = server_socket.accept()

        # Handle the client connection in a separate thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    run_server('localhost', 8888)
