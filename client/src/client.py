from pprint import pprint
import socket
import os
import struct
import sys
import json
import threading
import numpy
import dxcam
import time
import platform
import wmi
import string
import psutil
import mouse
import os
import platform
import subprocess
import re
import pickle
import win32.win32api as win32api
import cpuinfo
import random
from termcolor import colored
from colorama import init
import cv2
import zlib
init()

CONFIG_PATH = os.path.join( os.path.expanduser("~"), ".linkcfg" )

class Logger:
    def __init__(self, prefix):
        self.prefix = prefix

    def log(self, arg, prefix="", *args):
        prefix = f"[{colored(self.prefix, 'blue') + colored('::' + prefix, 'white') if prefix else ''}]"
        out = f"{prefix} {arg} "
        for arg in args:
            out += f"{arg} "
        print(out)
    
    def error(self, arg, prefix="", *args):
        prefix = f"[{colored(self.prefix, 'red') + colored('::' + prefix, 'white') if prefix else ''}]"
        out = f"{prefix} {arg} "
        for arg in args:
            out += f"{arg} "
        print(out)

    def success(self, arg, prefix="", *args):
        prefix = f"[{colored(self.prefix, 'green') + colored('::' + prefix, 'white') if prefix else ''}]"
        out = f"{prefix} {arg} "
        for arg in args:
            out += f"{arg} "
        print(out)

    def warn(self, arg, prefix="", *args):
        prefix = f"[{colored(self.prefix, 'yellow') + colored('::' + prefix, 'white') if prefix else ''}]"
        out = f"{prefix} {arg} "
        for arg in args:
            out += f"{arg} "
        print(out)

class LinkUtilities:
    """
        Collection of commonly used methods for gathering data and interacting
        with the Project Link API
    """
    @staticmethod
    def GetLabeledDrives() -> list[dict]:
        drives = []
        drive_letters = string.ascii_uppercase
        for letter in drive_letters:
            if os.path.exists(f"{letter}:"):
                path = f"{letter}:\\"
                drives.append(
                    {
                        "path": path,
                        "label": win32api.GetVolumeInformation(path)[0]
                    }
                )
        return drives

    @staticmethod
    def GetUUID() -> str:
        random_ID = "".join([random.choice("abcdef"+string.digits) for x in range(16)])
        if not os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'w') as f:
                f.write(random_ID)
            return random_ID
        else:
            return open(CONFIG_PATH).read()

class RealtimeDataService:
    """
        A service which efficiently provides data from the system
    """
    def __init__(self) -> None:
        self.connected_devices = []
        self.storage_locations = []
        self.logger = Logger("RealtimeDataService")

        self.cpu = cpuinfo.get_cpu_info()
        self.logger.success('Collected CPU information', "init")

        # Expensive tasks mitigation
        self.relief_thread = threading.Thread(target=self._expensive_data_thread)
        self.relief_thread.daemon = True    # prevents locking program upon exit
        self.relief_thread.start()


    def _expensive_data_thread(self) -> list[dict]:
        """
        Thread worker for collecting data that doesnt update frequently, but still updates.
        These tasks are migrated to a thread to prevent excessive blocking on the main thread.
        """
        # print(f'[threaded-service] started service: _expensive_data_thread')
        self.logger.success('started service: _expensive_data_thread', "threaded-service")
        try:
            while True:
                try:
                    c = wmi.WMI()
                    devices = c.Win32_PnPEntity()
                    connected_devices = []
                    for device in devices:
                        connected_devices.append({
                            "name": device.name,
                            "description": device.description,
                            "status": device.status
                        })
                    self.connected_devices = connected_devices
                except Exception as e:
                    # print(f"[RT-expensive-data] can't gather device information: {e}")
                    self.logger.error(f"can't gather device information: {e}", "threaded-service")

                try:
                    storage = LinkUtilities.GetLabeledDrives()
                    self.storage_locations = storage
                except Exception as e:
                    # print(f"[RT-expensive-data] failed to enumerate storage locations: {e}")
                    self.logger.error(f"failed to enumerate storage locations: {e}", "threaded-service")
                time.sleep(10)
        except KeyboardInterrupt:
            self.logger.log("exiting service: _expensive_data_thread", "threaded-service")
            

    def GetStaticData(self) -> dict:
        """
        Returns basic system information
        """
        data_shard = {
            "os": f"{platform.system()} {platform.release()}",
            "memory": {
                # "used": f"{(psutil.virtual_memory().used / 1024 / 1024 / 1024):.2f} GB",
                "total": f"{(psutil.virtual_memory().free / 1024 / 1024 / 1024):.2f} GB"
            },
            "cpu": {
                "type": f"{self.cpu['brand_raw']}",
                "count": os.cpu_count(),
                # "used": f"{psutil.cpu_percent()}%"
            },
            # "storage": storage,
            "misc": {
                "user": os.getlogin()
            }
        }
        return data_shard


    def GetDynamicData(self) -> dict:
        """
        Return data that typically changes constantly which can be used for
        remote control
        """
        data_shard = {
            "used_memory": f"{(psutil.virtual_memory().used / 1024 / 1024 / 1024):.2f} GB",
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "storage_devices": self.storage_locations,
            "connected_devices": self.connected_devices,
            "mouse_position": mouse.get_position(),
            # "display_output": camera.get_latest_frame(),
        }
        return data_shard

class DisplayBuffer:
    def __init__(self, monitor: int = 0, fps: int = 15) -> None:
        self.monitor_id = monitor
        self.fps = fps
        self.camera = dxcam.create(monitor, 0, output_color="BGR")
        self.camera.start(video_mode=True, target_fps=fps)

        self._buffer = []
        self.camera_thread = threading.Thread(target=self._update_thread)
        self.camera_thread.daemon = True

        self.logger = Logger("DisplayBuffer")

        # start the thread
        self.camera_thread.start()
        self.running = True # This saves performance when the display buffer is not needed

    def get_latest_frame(self):
        if len(self._buffer) == 0:
            return None
        return self._buffer[-1]

    def _update_thread(self):
        self.logger.success('started service: _update_thread', "threaded-service")
        try:
            while True:
                if self.running:
                    self._buffer.append(self.camera.get_latest_frame())
                
                time.sleep(1/self.fps)
        except KeyboardInterrupt:
            self.camera.stop()
            del self.camera
            self.logger.log("exiting service: _update_thread", "threaded-service")

    def SetMonitor(self, monitor: int):
        self.monitor_id = monitor
        self.camera.stop()
        self.camera = dxcam.create(monitor, 0, output_color="BGR")
        self.camera.start(video_mode=True, target_fps=self.fps)

class SocketAPI:
    # TODO: Add encryption key parameter
    def __init__(self, host: str = "127.0.0.1", port: int = 5000) -> None:
        self.host = host
        self.port = port
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
        data = data[4:]
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
        
        # get the rest of the data
        data += self.socket.recv(struct.unpack("I", data)[0])
        return self.load_packet(data)

    def get(self, data: dict) -> dict:
        packed = self.create_packet(data)
        self.socket.send(packed)
        return self.recv()


global_logger = Logger("Project-Link")

UUID = LinkUtilities.GetUUID()

# 
#  SERVICES
# 

global_logger.log("initiating services", "core")

display = DisplayBuffer()

# RealtimeDataService: This is a service that provides organized data about the system
realtime = RealtimeDataService()

# 
#  RUNTIME LOOP
# 
class RuntimeManager:
    def __init__(self):
        # DisplayBuffer: This is a service that will be used to capture the screen
        self.display = DisplayBuffer()

        # RealtimeDataService: This is a service that provides organized data about the system
        self.realtime_data = RealtimeDataService()

        self.logger = Logger("Runtime")

    def _loop(self):
        self.logger.success("Started runtime loop", "threaded-service")




# try:
#     while True:
#         frame = display.get_latest_frame()
#         if frame is not None:
#             frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
#             cv2.imshow('frame', frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#         else:
#             time.sleep(1)

# except KeyboardInterrupt:
#     sys.exit(0)










# try:
#     # test = RealtimeService.GetDynamicData()
#     static_data = realtime.GetStaticData()
#     while True:
#         test = services["realtime"].GetDynamicData()
#         time.sleep(.1)

# except KeyboardInterrupt:
#     global_logger.log("Exiting Project-Link Client", "core")
#     sys.exit(0)