import time
import json
import os
from datetime import datetime
import ctypes
from ctypes import wintypes

# PATH SETUP

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(BASE_DIR, "state")
STATE_FILE = os.path.join(STATE_DIR, "screen_state.json")

os.makedirs(STATE_DIR, exist_ok=True)

# WIN32 SETUP 

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

# ------------------ STATE ------------------

last_hwnd = None
last_process = None
screen_change_count = 0

CHECK_INTERVAL = 0.5 

# ------------------ HELPERS ------------------
def get_foreground_process():
    hwnd = user32.GetForegroundWindow()
    # print("[DEBUG] HWND:", hwnd)

    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    # print("[DEBUG] PID:", pid.value)

    return hwnd, pid.value


def write_state():
    data = {
        "screen_change_count": screen_change_count,
        "last_update": datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    }
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ------------------ MAIN LOOP ------------------

def run():

    hwnd, pid = get_foreground_process()
    # print("[DEBUG] Returned:", hwnd, pid)

    global last_hwnd, last_process, screen_change_count

    print("[screen_detect] Foreground app tracking started")

    try:
        while True:
            hwnd = user32.GetForegroundWindow()
            # print("[DEBUG]", hwnd)
            hwnd, process_name = get_foreground_process()

            if hwnd and process_name:
                if hwnd != last_hwnd:
                    screen_change_count += 1
                    last_hwnd = hwnd
                    last_process = process_name

                    print(
                        f"[screen_detect] App switch → {process_name} "
                        f"(count={screen_change_count})"
                    )

                    write_state()

            time.sleep(CHECK_INTERVAL)
        

    except KeyboardInterrupt:
        write_state()
        print("[screen_detect] stopped")

if __name__ == "__main__":
    run()