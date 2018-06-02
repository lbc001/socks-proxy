'''
handle the sock5 data.
'''
import socket

def HandleSocks5Verify(data):
    #print(data)
    #assert(data == b"\x05\x01\x00")
    return b"\x05\x00"

def HandleSocks5RequestData(data):
    '''
    handle the socks5 request data, return the domain/ip, port.
    '''
    assert(data[0] == 0x05)
    assert(data[1] == 0x01) # only handle CONNECT REQUEST
    request_type = data[3]
    addr, port = None, None
    if request_type == 0x01:
        addr = socket.inet_ntoa(data[4:8])
        port = int.from_bytes(data[8:10], "big")
    elif request_type == 0x03:
        domian_length = data[4]
        addr = data[5:5+domian_length]
        port = int.from_bytes(data[5+domian_length:7+domian_length], "big")
    return addr, port

def BuildReplyData(addr, port):
    '''
    build reply data with addr and port.
    '''
    reply = b"\x05\x00\x00\x01"
    reply += socket.inet_aton(addr) + int.to_bytes(port, 2, "big") # addr is only the ip format.
    return reply

def BuildConnectRefuseData():
    '''
    return the Connect Refused Reply.
    '''
    return b"\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00"

