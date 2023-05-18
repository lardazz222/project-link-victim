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
        self.logger = Logger("SocketAPI", debug=True)
        # try:
        #     self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     self.socket.connect((self.host, self.port))
        #     self.logger.success(f"connected to {self.host}:{self.port}", "socket")
        # except Exception as e:
        #     self.logger.error(f"failed to connect to {self.host}:{self.port}: {e}", "socket")
        #     sys.exit(1)

    # TODO: Add methods to interact with ProjectLink server. It functions
    #       
    #       get(data):
    #           - Send a request to the server
    #           - Return a response from the server
    #
    #       Custom methods will be created to abstractify the process of API interaction

    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.logger.success(f"connected to {self.host}:{self.port}", "socket")
            return True
        except:
            self.logger.error(f"failed to connect to {self.host}:{self.port}", "socket")
            return False
        
    def auto_reconnect(self):
        """
        Lock the thread until a connection is established
        """
        while True:
            # check if socket is connected already
            if self.connect():
                break
            time.sleep(1)

    def recv(self, buffer: int = 4096):
        try:
            header = self.socket.recv(4)
            if not header:
                return None

            data_len = struct.unpack("!I", header)[0]
            data = b""
            while data_len > 0:
                chunk = self.socket.recv(min(buffer, data_len))
                if not chunk:
                    break
                data += chunk
                data_len -= len(chunk)

            return data
        except socket.error as e:
            self.logger.error(f"Failed to recieve data ({e})", "socket")
            return None

    def send(self, data: dict) -> None:
        """
        Send data to the client.

        :param data: data to send to the client
        """
        data = zlib.compress(pickle.dumps(data))
        data_len = len(data)
        header = struct.pack("!I", data_len)
        try:
            self.socket.sendall(header)
            sent = 0
            while sent < data_len:
                sent += self.socket.send(data[sent:])
        except socket.error as e:
            # Handle send error
            self.logger.error(f"Failed to send data ({e})", "socket")
            return None
    def get(self, data: dict) -> dict:
        data['uuid'] = UUID
        self.send(data)
        response = self.recv()
        if not response:
            return None
        response = pickle.loads(zlib.decompress(response))
        return response

    def close(self):
        self.socket.close()

    # Called when the client starts. This tells the server the unique ID, for referencing
    def Register(self):
        data = {
            "type": "register",
            "data": {
                "static_data": RealtimeDataService().GetStaticData(),
                "dynamic_data": RealtimeDataService().GetDynamicData(),
                "uuid": UUID
            }
        }
        return self.get(data)

    def UpdateDynamicData(self, data: dict) -> dict:
        data = {
            "type": "update_dynamic",
            "data": data
        }
        return self.get(data)

    def UpdateStaticData(self, data: dict) -> dict:
        data = {
            "type": "update_static",
            "data": data
        }
        return self.get(data)

    def Ping(self) -> dict:
        data = {
            "type": "ping"
        }
        return self.get(data)

    def CanStream(self) -> bool:
        return self.get(
            {
                "type": "canStream",
            }
        )['data']

    def UpdateStreamBuffer(self, frame: np.ndarray) -> dict:
        return self.get(
            {
                "type": "updateStreamBuffer",
                "data": frame
            }
        )
    
    def Disconnect(self) -> None:
        # send disconnect signal to server,
        # this helps keep it clean
        self.send(
            {
                "type": "disconnect",
            }
        )