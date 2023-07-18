import queue
import uuid
import enum
import socket
from _thread import start_new_thread


class ProcessorStatusEnum(enum.Enum):
    Start = 1
    Stop = 2
    Terminating = 3

class Processor:
    queue = None
    threads: int
    processes = []
    wait_timeout = 5
    
    def __init__(self, threads=1):
        self.queue = queue.Queue()
        self.threads = threads
    
    def add_process(self, connection, address, data):
        self.queue.put({'connection': connection, 'address': address, 'data': data})
    
    def start(self):
        for i in range(self.threads):
            start_new_thread(self.start_new_process, ())
    
    def start_new_process(self):
        id = uuid.uuid4()
        self.processes.append({'id': id, 'status': ProcessorStatusEnum.Start})
        while True:
            try:
                item = self.queue.get(True, self.wait_timeout)
                connection = item['connection']
                address = item['address']
                data = item['data']

                if data:
                    self.process_data(connection, address, data)
                
                self.queue.task_done()

            except queue.Empty:
                if self.should_stop(id):
                    self.stop(id)
                    break
    
    def process_data(self, connection, address, data):
        try:
            print('==================')
            print(f'address: {address}')
            print(f'data: {data}')
            print('==================')
            connection.send(b'ok')

        except (BrokenPipeError, ConnectionError, ConnectionResetError):
            print('client disconnected!')
    
    def should_stop(self, id):
        for process in self.processes:
            if process['id'] == id:
                return process['status'] == ProcessorStatusEnum.Terminating
        return False
    
    def terminate(self, id):
        for process in self.processes:
            if process['id'] == id:
                process['status'] = ProcessorStatusEnum.Terminating

    def stop(self, id):
        for process in self.processes:
            if process['id'] == id:
                process['status'] = ProcessorStatusEnum.Stop
                print(f'stopping process {process["id"]}')

    def stop_all_process(self):
        for process in self.processes:
            process['status'] = ProcessorStatusEnum.Terminating
