from .imports import *
from .Logger import Logger
from .JobHandler import JobHandler
from .DisplayBuffer import DisplayBuffer
from .RealtimeDataService import RealtimeDataService
from .Utilities import Utilities


UUID = Utilities.GetUUID()

class SocketAPI:
    # TODO: Add encryption key parameter
    def __init__(self, job_handler: JobHandler,host: str = "127.0.0.1", port: int = 5000) -> None:
        self.host = host
        self.port = port
        self.job_handler = job_handler
        self.logger = Logger("SocketAPI")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.logger.success(f"connected to {self.host}:{self.port}", "socket")
        except Exception as e:
            self.logger.error(f"failed to connect to {self.host}:{self.port}: {e}", "socket")
            sys.exit(1)

    # TODO: Add methods to interact with ProjectLink server. It functions
    #       
    #       get(data):
    #           - Send a request to the server
    #           - Return a response from the server
    #
    #       Custom methods will be created to abstractify the process of API interaction

    def create_packet(self, data: dict) -> bytes:
        """
        Assemble a packet made of bytes before sending to server
        """
        data = pickle.dumps(data)
        data = zlib.compress(data)

        packet = b""
        packet += struct.pack("I", len(data))
        packet += data
        return data

    def load_packet(self, data: bytes) -> dict:
        data = zlib.decompress(data) # decompress
        data = pickle.loads(data) # convert to python object
        if not isinstance(data, dict):
            raise TypeError(f"expected data to be of type dict, got {type(data)}")
        return data

    def recv(self) -> dict:
        # get first 4 bytes
        data = self.socket.recv(4)
        if not data:
            return None
        # remove first 4 bytes
        data = data[4:]
        # get the rest of the data
        data += self.socket.recv(struct.unpack("I", data)[0])
        return self.load_packet(data)

    def get(self, data: dict) -> dict:
        data['uuid'] = UUID
        packed = self.create_packet(data)
        self.socket.send(packed)
        return self.recv()
    
    def close(self):
        self.socket.close()

    # Called when the client starts. This tells the server the unique ID, for referencing
    def Register(self):
        data = {
            "type": "register",
        }
        return self.get(data)
    
    def GetJobs(self) -> dict:
        self.logger.log("fetching jobs", "socket")
        data = {
            "type": "get-jobs",
        }
        return self.get(data)
    
    def MarkJobAsComplete(self, job_id):
        self.logger.log(f"marking job {job_id} as complete", "socket")
        data = {
            "type": "complete_job",
            "job_id": job_id
        }
        return self.get(data)
