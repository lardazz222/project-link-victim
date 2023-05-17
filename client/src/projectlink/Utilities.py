from .imports import *
from .Logger import Logger
from .imports import CONFIG_PATH

class Utilities:
    """
        Static class collection of commonly used methods for gathering data and interacting
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

