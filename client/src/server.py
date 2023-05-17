import socket
import threading
import sys
import time
import os
import pickle
import zlib

class Client:
    def __init__(self, sock: socket.socket, addr: tuple, unique_id: str):
        """
        Client class to manage live connections and data throughput.

        :param sock: socket object
        :param addr: tuple of (ip, port)
        :param unique_id: unique id of client. this is generated client side just for referencing
        """
        self.sock = sock
        self.addr = addr
        self.unique_id = unique_id

        self.connected = True
        self.last_ping = time.time()

        self.dynamic_data = {}
        self.static_data = {}


class ClientManager:
    def __init__(self) -> None:
        self.clients = []
        self.client_lock = threading.Lock()

    def add_client(self, client: Client) -> None:
        self.client_lock.acquire()
        self.clients.append(client)
        self.client_lock.release()
        
    def remove_client(self, client: Client) -> None:
        self.client_lock.acquire()
        self.clients.remove(client)
        
        
    