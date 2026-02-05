import threading
import time
from modules.app_and_process_blocker import process_blocker
from modules.broadcast import fullscreen_image_slideshow
from modules.input_blocker import block_input_15min
from modules.external_device_detector import start_usb_watcher
from modules.keylog import start_keyboard_logger as _start_keyboard_logger
from modules.screenshotwithtabdetection import (
    start as _start_screen,
    stop as _stop_screen,
    is_alive as screen_is_alive
)

from analysis_modules.ocr.ocr import start_ocr_service
from analysis_modules.cheating_analysis.raw_data_collector import (
    start_raw_data_collector,
    stop_raw_data_collector
)




# feature flags
p1 = True    # process blocker
p2 = False   # slideshow
p3 = False   # input blocker (15 min)
p4 = True    # USB detector
p5 = True    # keyboard logger
p6 = True    # screen capture + tab detection
p7 = True    # OCR service
p8 = True    # raw data collector


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
    start_usb_watcher(on_usb_connected, on_usb_disconnected)


def start_keyboard_logger_worker():
    t = threading.Thread(
        target=_start_keyboard_logger,
        daemon=True
    )
    t.start()
    return t


def start_screen_capture_worker():
    t = threading.Thread(
        target=_start_screen,
        daemon=True
    )
    t.start()
    return t


def start_ocr_worker():
    t = threading.Thread(
        target=start_ocr_service,
        daemon=True
    )
    t.start()
    return t


def start_raw_data_worker():
    t = threading.Thread(
        target=start_raw_data_collector,
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
    ocr_thread = None
    raw_thread = None

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

    # OCR starts ONLY based on flag dependency (NO aliveness check)
    if p7 and p6:
        ocr_thread = start_ocr_worker()

    # Raw data starts ONLY if screenshot + OCR flags are enabled
    if p8 and p6 and p7:
        raw_thread = start_raw_data_worker()


    while True:
        
        time.sleep(5)

        if p1 and pb_thread and not pb_thread.is_alive():
            print("[orchestrator] process blocker died")

        if p2 and slideshow_thread and not slideshow_thread.is_alive():
            print("[orchestrator] slideshow died")

        if p3 and input_blocker_thread and not input_blocker_thread.is_alive():
            print("[orchestrator] input blocker finished")

        if p5 and keyboard_thread and not keyboard_thread.is_alive():
            print("[orchestrator] keyboard logger died")

        if p6 and not screen_is_alive():
            print("[orchestrator] screen capture died")

        if p7 and ocr_thread and not ocr_thread.is_alive():
            print("[orchestrator] OCR service died")

        if p8 and raw_thread and not raw_thread.is_alive():
            print("[orchestrator] raw data collector died")



if __name__ == "__main__":
    main()
