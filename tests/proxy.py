import socket
import requests
import ssl
from src import get_the_dst_ip

def recvall(sock, buffer_size):
    '''
    recv all the data from the socket
    '''
    data = b""
    while True:
        part = sock.recv(buffer_size)
        data += part
        if len(part) < buffer_size:
            break
    return data

def handle(conn):
    data = recvall(conn, 1024)
    if data == b'\x05\x01\x00':
        conn.send(b'\x05\x00')
    data = recvall(conn, 1024)
    domain_string = data[5:5+data[4]].decode("utf-8")
    port = int.from_bytes(data[5+data[4]:7+data[4]], "big")
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((domain_string, port))
    local = remote_socket.getsockname()
    send_data = b"\x05\x00\x00\x01" + socket.inet_aton(local[0]) + local[1].to_bytes(2, "big")
    conn.send(send_data)
    while True:
        data = recvall(conn, 1024)
        if data == b"":
            break
        print(data)
        remote_socket.send(data)
        recv_data = recvall(remote_socket, 1024)
        if recv_data == b"":
            break
        conn.send(recv_data)
        print(recv_data)

mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysocket.bind(("127.0.0.1", 8000))
mysocket.listen(1)

while True:
    conn, address = mysocket.accept()
    print(address)
    handle(conn)