'''
test socket forwarding.
'''
import socket
import select

class TransferServer:
    '''
    the transfer server code
    '''
    def __init__(self, ip, port, remote_ip, remote_port):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((ip, port))
        self._socket.listen(1)
        self._socket.setblocking(0)
        self._buffer_size = 1024
        self._epoll = select.epoll()
        self._epoll.register(self._socket.fileno(), select.EPOLLIN|select.EPOLLET)
        self._fd_to_socket = {self._socket.fileno():self._socket}
        self._remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._remote_socket.connect((remote_ip, remote_port))
        self._requests = {}

    def transfer(self, data):
        '''
        transfer the data to the remote host.
        '''
        self._remote_socket.send(data)
        recv_data = self._remote_socket.recv(1024)
        return recv_data

    def start(self):
        '''
        start the epoll events.
        '''
        while True:
            events = self._epoll.poll(-1)
            for fd, event in events:
                socket = self._fd_to_socket[fd]
                if socket == self._socket:
                    conn, add = self._socket.accept()
                    conn.setblocking(0)
                    self._epoll.register(conn.fileno(), select.EPOLLIN|select.EPOLLET)
                    self._fd_to_socket[conn.fileno()] = conn
                elif event & select.EPOLLIN:
                    data = socket.recv(self._buffer_size)
                    if data == b"":
                        self._epoll.unregister(fd)
                        self._fd_to_socket[fd].close()
                        del self._fd_to_socket[fd]
                        continue
                    self._requests[fd] = self.transfer(data)
                    self._epoll.modify(fd, select.EPOLLOUT)
                elif event & select.EPOLLOUT:
                    socket.send(self._requests[fd])
                    self._epoll.modify(fd, select.EPOLLIN)

demo = TransferServer("127.0.0.1", 8011, "127.0.0.1", 8080)
demo.start()