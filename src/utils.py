'''
define the util functions.
'''

def recvall(socket, buffer_size):
    '''
    recv all data from the socket
    '''
    data = b""
    while True:
        try:
            part = socket.recv(buffer_size)
            data += part
            if len(part) < buffer_size:
                break
        except:
            continue
    return data