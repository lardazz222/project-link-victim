from .imports import *
from .Logger import Logger
from .Utilities import Utilities



class RealtimeDataService:
    """
        A singleton service which efficiently provides data from the system
    """
    instance = None

    def __new__(cls) -> object:
        if RealtimeDataService.instance is None:
            RealtimeDataService.instance = object.__new__(cls)
            return RealtimeDataService.instance
        else:
            return RealtimeDataService.instance
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
                    storage = Utilities.GetLabeledDrives()
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
