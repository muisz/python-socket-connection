import socket
import enum

from app.client_handler import ClientHandler
from app.processor import Processor
from app.logging import get_system_log


class AppStatus(enum.Enum):
    Start = 1
    Stop = 2

class App:
    host: str
    port: int
    socket = None

    status: AppStatus

    handler: ClientHandler
    processor: Processor

    sys_log = None

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.processor = Processor()
        self.handler = ClientHandler(self.processor)
        self.sys_log = get_system_log()
    
    def start(self):
        self.start_socket()
        self.handler.start()
        self.processor.start()
        self.accept_connections()

    def start_socket(self):
        self.socket = socket.socket()
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        self.status = AppStatus.Start
        self.sys_log.info(f'server started on {self.host}:{self.port}')

    def accept_connections(self):
        while True:
            connection, address = self.socket.accept()
            self.handler.add_client(connection, address)
            self.sys_log.info(f'connected with {address}')

    def stop(self):
        self.socket.close()
        self.handler.stop()
        self.processor.stop_all_process()
