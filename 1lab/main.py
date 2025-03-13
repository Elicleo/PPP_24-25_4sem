import struct
import socket
import os
import logging
import threading
import sys
import time
from abc import ABC, abstractmethod
import json

HOST = 'localhost'
PORT = 12346

file_handler = logging.FileHandler(filename='tmp.log')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [stdout_handler]

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(name)s - %(message)s',
    handlers=handlers
)


class RecvSendMsgsProtocol(ABC):
    MSG_SIZE = 16

    @abstractmethod
    def recv(self, connected_socket):
        return ''

    @abstractmethod
    def send(self, connected_socket, text):
        pass


class Node:
    def __init__(self, data):
        self.data = data
        self.descendants = []

    def add_desc(self, desc_node):
        if type(desc_node) == list:
            for d in desc_node:
                new_node = Node(d)
                self.descendants.append(new_node)
        else:
            self.descendants.append(desc_node)


class Tree:
    def __init__(self):
        self.root = None
        self.json_like = {}

    def insert(self, data):
        directories = data[0].split('\\')
        if self.root is None:
            self.root = Node(directories[0])
        current = self.root
        for i, d in enumerate(directories):
            for desc in current.descendants:
                if d == desc.data:
                    current = desc
                    break
            else:
                new_node = Node(d)
                current.add_desc(new_node)
                current = new_node
        current.add_desc(data[1])
        self.to_json(data)

    def to_json(self, data):
        directories = data[0].split('\\')
        if len(self.json_like) == 0:
            self.json_like[directories[0]] = []
        try:
            current = self.json_like[directories[0]]
        except:
            # print(directories[0])
            # print(self.json_like)
            # directories[0][0] = directories[0].upper()
            current = self.json_like[directories[0].upper()]
        for i, d in enumerate(directories[1:]):
            for value in current:
                if d == value:
                    current = value.keys()
                    break
            else:
                sl = {d: []}
                current.append(sl)
                current = sl[d]
        current.append(data[1])

        with open('Env_exe_info.json', mode='w', encoding='utf-8') as f:
            json.dump(self.json_like, f, indent=2)

    def show(self):
        to_return = ''
        if self.root is not None:
            current = self.root
            for desc in current.descendants:
                to_return += self._display(desc, 0)
        return to_return

    def _display(self, node, lev):
        extensions = ['.exe', '.bat', '.com']
        to_return = '\n' + '   ' * (lev) + '-> ' + node.data if lev > 0 else '\n' + '   ' * (lev) + node.data
        if not node.descendants:
            pass
        else:
            for desc in node.descendants:
                to_return += self._display(desc, lev + 1)
        return to_return


class Server:
    def __init__(self, protocol_handler, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.protocol_handler = protocol_handler
        self.logger = logging.getLogger('Server')

    def handle_client(self, client_socket):
        while True:
            recv_text = self.protocol_handler.recv(client_socket)
            if not recv_text:
                break
            self.logger.info(f'recv "{recv_text}"')
            if 'rename' in recv_text:
                old, new = recv_text.split('\n')[0][7:-1].split(', ')
                self.renaming(old, new)
                send_text = 'renaming done'
                self.protocol_handler.send(client_socket, send_text)
                self.logger.info(f'send "{send_text}"')
            elif 'update' in recv_text.lower():
                self.search_exe()
                send_text = 'information updated'
                self.protocol_handler.send(client_socket, send_text)
                self.logger.info(f'send "{send_text}"')
            elif 'file' in recv_text.lower():
                send_text = os.getcwd() + '\\Env_exe_info.json'
                self.protocol_handler.send(client_socket, send_text)
                self.logger.info(f'send "{send_text}"')
            elif 'show' in recv_text.lower():
                send_text = self.tree.show()
                self.protocol_handler.send(client_socket, send_text)
                self.logger.info(f'send "{send_text}"')
            else:
                send_text = 'unknown command'
                self.protocol_handler.send(client_socket, send_text)
                self.logger.info(f'send "{send_text}"')

    def run(self):
        self.search_exe()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            self.logger.info(f'started on {(self.host, self.port)}')
            s.listen(1)
            client, addr = s.accept()
            with client:
                self.logger.info(f'connect {addr}')
                self.handle_client(client)

            self.logger.info(f'closed on {(self.host, self.port)}')

    def search_exe(self):
        self.env = os.environ
        extensions = ['exe', 'bat', 'com']
        self.exe_files = []
        self.tree = Tree()
        for directory in os.environ['PATH'].split(';'):
            if os.path.isdir(directory):
                for file in os.listdir(path=directory):
                    if any(file[-3:] == ex for ex in extensions):
                        self.exe_files.append(directory)
                        self.tree.insert((directory, [i for i in os.listdir(path=directory) if
                                                      any(i[-3:] == ex for ex in extensions)]))
                        break

    def renaming(self, old, new):
        os.rename(old, new)
        self.search_exe()


class Client:
    def __init__(self, protocol_handler, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.protocol_handler = protocol_handler
        self.logger = logging.getLogger('Client')

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            while True:
                to_send = input('Enter command:\n')
                if to_send:
                    send_text = to_send
                    self.protocol_handler.send(s, send_text)
                    self.logger.info(f'send "{send_text}"')
                    recv_text = self.protocol_handler.recv(s)
                    self.logger.info(f'recv "{recv_text}"')
                else:
                    break


class Protocol(RecvSendMsgsProtocol):
    def recv(self, connected_socket):
        res_data = b''
        data = connected_socket.recv(self.MSG_SIZE)
        connected_socket.setblocking(False)
        while data:
            res_data += data
            try:
                data = connected_socket.recv(self.MSG_SIZE)
            except:
                break
        connected_socket.setblocking(True)
        connected_socket.send(b'ok')
        return res_data.decode()

    def send(self, connected_socket, text):
        connected_socket.sendall(text.encode())
        response = connected_socket.recv(self.MSG_SIZE).decode()
        if response != 'ok':
            pass


def test(protocol_cls):
    server = Server(protocol_cls())
    client = Client(protocol_cls())

    t_s = threading.Thread(target=Server.run, args=[server])
    t_c = threading.Thread(target=client.run, args=[])
    t_s.start()
    time.sleep(1)
    t_c.start()
    t_c.join()
    t_s.join()


if __name__ == "__main__":
    # print('hi')
    test(Protocol)
