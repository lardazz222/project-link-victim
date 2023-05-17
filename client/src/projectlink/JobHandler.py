from .imports import *
from .Logger import Logger
from .DisplayBuffer import DisplayBuffer
from .RealtimeDataService import RealtimeDataService
from .Utilities import Utilities


class JobHandler:
    def __init__(self):
        self.logger = Logger("JobHandler")
        self.jobs = []
        self.finished_jobs = []

        # self.job_handler_thread = threading.Thread(target=self._job_handler_loop)
        # self.job_handler_thread.daemon = True

        # self.job_handler_thread.start()
        self.JOB_OK = {
            "status": True
        }

        self.UNKNOW_JOB_TYPE = {
            "status": False,
            "message": "unknown job type"
        }

        self.buffer = DisplayBuffer() # This is a singleton meaning that it will only be created once if the constructor is called multiple times, it will return the same instance
        self.realtime_data = RealtimeDataService()
    

    def ProcessJob(self, job: dict):
        job_type = job['type']
        match job_type:
            case "mouse":
                x = job['x']
                y = job['y']
                self.logger.debug(f"X:{x} Y:{y}", "mouse")
                return self.JOB_OK
            case "ping":
                self.logger.debug("ping", "ping")
                return self.JOB_OK
            case "static_data":
                self.logger.debug("static_data", "static_data")
                OK = self.JOB_OK
                OK['response'] = self.realtime_data.GetStaticData()
                return OK
            case "dynamic_data":
                self.logger.debug("dynamic_data", "dynamic_data")
                OK = self.JOB_OK
                OK['response'] = self.realtime_data.GetDynamicData()
                return OK
            case "display":
                self.logger.debug("display", "display")
                OK = self.JOB_OK
                OK['response'] = self.buffer.get_latest_frame_and_compress()
                return OK
            case _:
                self.logger.error(f"unknown job type: {job_type}", "job-handler")

        return self.UNKNOW_JOB_TYPE
