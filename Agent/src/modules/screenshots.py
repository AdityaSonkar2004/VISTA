import threading
import time
from datetime import datetime
from mss import mss
from PIL import Image
from io import BytesIO
import os
from uuid import uuid4


_capture_thread = None
_running = False
_last_thumbnail = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOT_DIR = os.path.join(BASE_DIR, "ss")

INTERVAL = 1.0  
SESSION_ID = uuid4().hex[:6].upper()



def _capture_loop():
    global _last_thumbnail, _running

    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    with mss() as sct:
        monitor = sct.monitors[0]

        while _running:
            t_start = time.monotonic()

            try:
                frame = sct.grab(monitor)
                img = Image.frombytes("RGB", frame.size, frame.rgb)

                timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                filename = f"{timestamp}_{SESSION_ID}.jpg"
                path = os.path.join(SCREENSHOT_DIR, filename)

                img.save(path, "JPEG", quality=80, subsampling=2)

                # thumbnail
                thumb = img.resize((500, 350))
                buf = BytesIO()
                thumb.save(buf, "JPEG", quality=50)
                _last_thumbnail = buf.getvalue()

            except Exception as e:
                print(f"Screenshot error: {e}")

            elapsed = time.monotonic() - t_start
            time.sleep(max(0, INTERVAL - elapsed))


def start():
    global _capture_thread, _running

    if _running:
        return False

    _running = True
    _capture_thread = threading.Thread(
        target=_capture_loop,
        name="ScreenshotThread",
        daemon=True,
    )
    _capture_thread.start()
    print("Screenshot module started")
    return True


def stop():
    global _running, _capture_thread

    if not _running:
        return False

    _running = False
    if _capture_thread:
        _capture_thread.join(timeout=3)
    print("Screenshot module stopped")
    return True


def get_thumbnail():
    return _last_thumbnail or b""


def start_screen_capture_worker(interval):
    global INTERVAL
    INTERVAL = interval

    start()
    print("Running... Ctrl+C to stop")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop()


if __name__ == "__main__":
    start_screen_capture_worker(INTERVAL)
