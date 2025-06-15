import psutil
from icecap.constants import WOW_PROCESS_NAME


def find_linux_wow_process_id() -> int:
    for proc in psutil.process_iter(["pid", "name"]):
        if WOW_PROCESS_NAME.lower() in proc.info["name"].lower():
            return proc.info["pid"]
    raise ValueError("WoW process not found.")
