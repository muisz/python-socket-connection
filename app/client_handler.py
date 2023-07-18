import queue
import enum
import socket
from _thread import start_new_thread

from app.logging import get_system_log

class ClientHandlerStatusEnum(enum.Enum):
    Start = 1
    Stop = 2
    Terminating = 3

class ClientHandler:
    queue = None
    processor = None

    status: ClientHandlerStatusEnum

    client_timeout = 3

    sys_log = None

    def __init__(self, processor):
        self.queue = queue.Queue()
        self.processor = processor
        self.sys_log = get_system_log()

    def add_client(self, connection, address):
        self.queue.put({'connection': connection, 'address': address})

    def start(self):
        start_new_thread(self.start_handler, ())

    def start_handler(self):
        self.sys_log.info('client handler started')
        self.status = ClientHandlerStatusEnum.Start
        while True:
            try:
                item = self.queue.get(True, 5) # seconds
                connection = item["connection"]
                address = item["address"]
                
                try:
                    connection.settimeout(self.client_timeout) # seconds
                    data = connection.recv(1024)
                    self.processor.add_process(connection, address, data)
                
                except (BrokenPipeError, ConnectionResetError):
                    self.queue.task_done()
                    self.sys_log.warn(f'cannot send data. client {address} disconnected')
                    continue

                except socket.timeout:
                    pass
                    
                self.add_client(connection, address)
                self.queue.task_done()

            except queue.Empty:
                if self.should_stop():
                    self.stop()
                    break
    
    def should_stop(self):
        return self.status == ClientHandlerStatusEnum.Terminating
    
    def terminate(self):
        self.status = ClientHandlerStatusEnum.Terminating
    
    def stop(self):
        self.status = ClientHandlerStatusEnum.Stop
        self.sys_log.info("stopping client handler")
