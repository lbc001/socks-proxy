import socket
import requests

def recvall(socket, buffer_size):
    '''
    recv all the data from the socket
    '''
    data = b""
    while True:
        part = socket.recv(buffer_size)
        data += part
        if len(part) < buffer_size:
            break
    return data

def handle(conn):
    data = recvall(conn, 1024)
    if data == b'\x05\x01\x00':
        conn.send(b'\x05\x00')
    print(recvall(conn, 1024))

mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysocket.bind(("127.0.0.1", 8000))
mysocket.listen(1)

while True:
    conn, address = mysocket.accept()
    handle(conn)