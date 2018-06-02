import socket
import time

test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
test_sock.setblocking(False)
connect_ex = test_sock.connect_ex(('1.2.3.4', 80))
print(connect_ex)