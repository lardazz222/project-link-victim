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

# TODO: Use a singleton class for displasy and realtime services
# from projectlink import Logger, DisplayBuffer, RealtimeDataService, JobHandler, SocketAPI, LinkUtilities
from projectlink.Logger import Logger
from projectlink.DisplayBuffer import DisplayBuffer
from projectlink.RealtimeDataService import RealtimeDataService
from projectlink.JobHandler import JobHandler
from projectlink.SocketAPI import SocketAPI
from projectlink.Utilities import Utilities
from projectlink.imports import CONFIG_PATH



UUID = Utilities.GetUUID()


global_logger = Logger("Project-Link")
global_logger.log("initiating services", "core")

class RuntimeManager:
    def __init__(self):
        self.logger = Logger("Runtime")
        self.display = DisplayBuffer() # This is a service that will be used to capture the screen
        self.realtime_data = RealtimeDataService() # This is a service that provides organized data about the system
        self.job_handler = JobHandler() # This is a service that will handle jobs
        self.api = SocketAPI(self.job_handler, host="127.0.0.1", port=6969)

    def Start(self) -> None:
        """
        Start the main application loop
        """
        self._loop()

    def OnInterval(self):
        dynamic_data = self.realtime_data.GetDynamicData()
        res = self.api.UpdateDynamicData(dynamic_data)
        
        if not res: # TODO: add more updates later (ex: screen capture)
            self.logger.error("Failed to update dynamic data", "core")
        else:
            self.logger.log(f"Update result: {res['status']}", "dynamic_data")

    def _loop(self):
        try:
            while True:
                self.api.auto_reconnect()

                reg_result = self.api.Register() # sends UUID, and system data
                if not reg_result:
                    self.logger.error("Failed to register", "core")
                    continue
                else:
                    pprint(reg_result['data'])
                
                interval = 0
                max_interval = 5
                try:
                    while True:
                        try:
                            pong = self.api.Ping()
                            if not pong:
                                break # stop the loop and try to reconnect
                        except ConnectionAbortedError:
                            break
                        
                        canStream = self.api.CanStream()
                        if canStream:
                            update_stream = self.api.UpdateStreamBuffer(self.display.get_latest_frame_and_compress())
                            if not update_stream:
                                self.logger.error("Failed to update stream buffer", "core")


                        # Happens every max_interval seconds
                        time.sleep(0.5)
                        interval += 1
                        if interval >= max_interval:
                            self.OnInterval()
                            interval = 0
                except ConnectionAbortedError:
                    self.logger.log("Disconnected", "runtime")
                time.sleep(1)               
        except KeyboardInterrupt:
            self.logger.log("CTRL+C: Exiting Project-Link Client", "core")
            # send a disconnect message to the server
            self.api.Disconnect()
            sys.exit(0)

if __name__ == "__main__":
    rt = RuntimeManager()
    rt.Start()