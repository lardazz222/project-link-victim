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
        # api = SocketAPI(self.job_handler, host="127.0.0.1", port=5000)

    def Start(self) -> None:
        """
        Start the main application loop
        """
        self._loop()

    def _loop(self):
        try:
            self.logger.success("Started runtime loop", "threaded-service")
            while True:
                # show latest frame
                frame = self.display.get_latest_frame()
                if frame is not None:
                    frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
                    cv2.imshow('frame', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        except KeyboardInterrupt:
            self.logger.log("Exiting Project-Link Client", "core")
            sys.exit(0)

if __name__ == "__main__":
    rt = RuntimeManager()
    rt.Start()


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