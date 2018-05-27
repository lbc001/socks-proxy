'''
the main proxy code in my project.
'''
import socket
import select
from .socks5 import HandleSocks5Verify, HandleSocks5RequestData, BuildReplyData, BuildConnectRefuseData
from .utils import recvall



class Proxy:
    '''
    the proxy server code.
    '''
    def __init__(self, ip, port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((ip, port))
        self._socket.listen(1)
        self._socket.setblocking(0)
        self._buffer_size = 1024
        self._epoll = select.epoll()
        self._epoll.register(self._socket.fileno(), select.EPOLLIN|select.EPOLLET)
        self._fd_to_socket = {self._socket.fileno():self._socket}
        self._fd_count = {}
        self._fd_to_fd = {}
        self._fd_reply = {}

    def start(self):
        while True:
            events = self._epoll.poll(-1)
            for fd,event in events:
                sock = self._fd_to_socket[fd]
                if sock == self._socket:
                    conn, _ = self._socket.accept()
                    conn.setblocking(0)
                    self._epoll.register(conn.fileno(), select.EPOLLIN|select.EPOLLET)
                    self._fd_to_socket[conn.fileno()] = conn
                    self._fd_count[conn.fileno()] = 0
                elif event & select.EPOLLIN:
                    data = recvall(sock, self._buffer_size)
                    if data == b"":
                        self._epoll.unregister(fd)
                        self._fd_to_socket[fd].close()
                    if fd in self._fd_count:
                        if self._fd_count[fd] == 0:
                            self._fd_reply[fd] = HandleSocks5Verify(data)
                            self._epoll.modify(fd, select.EPOLLOUT)
                        elif self._fd_count[fd] == 1:
                            try:
                                addr, port = HandleSocks5RequestData(data)
                                print(addr, port)
                                remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                remote_sock.setblocking(0)
                                remote_sock.connect((addr, port))
                            except socket.error:
                                self._fd_reply[fd] = BuildConnectRefuseData()
                                self._epoll.modify(fd, select.EPOLLOUT)
                                continue
                            self._epoll.register(remote_sock.fileno(), select.EPOLLIN|select.EPOLLET)
                            self._fd_to_fd[fd] = remote_sock.fileno()
                            self._fd_to_fd[remote_sock.fileno()] = fd
                            self._fd_to_socket[remote_sock.fileno()] = remote_sock
                            remote_addr, remote_port = remote_sock.getsockname()
                            self._fd_reply[fd] = BuildReplyData(remote_addr, remote_port)
                            self._epoll.modify(fd, select.EPOLLOUT)
                        else:
                            remote_fd = self._fd_to_fd[fd]
                            self._fd_reply[remote_fd] = data
                            #self._epoll.modify(fd, select.EPOLLOUT)
                            self._epoll.modify(remote_fd, select.EPOLLOUT)
                        self._fd_count[fd] += 1
                    else:
                        remote_fd = self._fd_to_fd[fd]
                        self._fd_reply[remote_fd] = data
                        #self._epoll.modify(fd, select.EPOLLOUT)
                        self._epoll.modify(remote_fd, select.EPOLLOUT)
                elif event & select.EPOLLOUT:
                    if fd in self._fd_reply and self._fd_reply[fd] != b"":
                        sock.send(self._fd_reply[fd])
                        if self._fd_reply[fd] == BuildConnectRefuseData():
                            self._epoll.unregister(fd)
                            self._fd_to_socket[fd].close()
                        else:
                            self._epoll.modify(fd, select.EPOLLIN)
                            self._fd_reply[fd] = b""
                    
                    


            