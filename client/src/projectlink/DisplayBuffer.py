from .imports import *
from .Logger import Logger

class DisplayBuffer:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not DisplayBuffer.instance:
            DisplayBuffer.instance = DisplayBuffer.__DisplayBuffer(*args, **kwargs)
        return DisplayBuffer.instance

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

    def get_latest_frame_and_compress(self, quality: int = 50):
        if len(self._buffer) == 0:
            return None
        return cv2.imencode('.jpg', self._buffer[-1], [cv2.IMWRITE_JPEG_QUALITY, quality])[1].tobytes()

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
