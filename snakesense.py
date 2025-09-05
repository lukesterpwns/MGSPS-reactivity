# SnakeSense - DualSense reactive lighting for MGS (DuckStation)
import threading
import time
import struct
from dataclasses import dataclass
from pydualsense import pydualsense
import pymem
import pymem.process

DUCKSTATION_PROCESS_NAME = "duckstation-qt-x64.exe"
ALERT_ADDR_CANDIDATES = [0x000B75B4, 0x080B75B4, 0x800B75B4, 0x100B75B4]
FLASH_DURATION_SEC = 15.0
FLASH_INTERVAL_SEC = 0.25

@dataclass
class FlashState:
    active: bool = False
    deadline: float = 0.0
    lock: threading.Lock = threading.Lock()

def find_duckstation_process():
    try:
        return pymem.Pymem(DUCKSTATION_PROCESS_NAME)
    except Exception:
        return None

def read_alert_counter(pm):
    for addr in ALERT_ADDR_CANDIDATES:
        for size in (2, 4):
            try:
                data = pm.read_bytes(addr, size)
                val = int.from_bytes(data, "little")
                if 0 <= val < 10000:
                    return val
            except Exception:
                continue
    return None

def flasher(ds: pydualsense, fstate: FlashState):
    toggle = False
    while True:
        with fstate.lock:
            now = time.time()
            active = fstate.active and now < fstate.deadline
            if not active:
                ds.light.setColorI(0, 0, 255)
        if active:
            if toggle:
                ds.light.setColorI(255, 0, 0)
            else:
                ds.light.setColorI(0, 0, 255)
            toggle = not toggle
            time.sleep(FLASH_INTERVAL_SEC)
        else:
            time.sleep(0.05)

def monitor_alerts(ds: pydualsense, fstate: FlashState):
    pm = None
    last_val = None
    while True:
        if pm is None:
            pm = find_duckstation_process()
            if pm is None:
                time.sleep(1.0)
                continue
        val = read_alert_counter(pm)
        if val is not None:
            if last_val is None:
                last_val = val
            elif val > last_val:
                with fstate.lock:
                    fstate.active = True
                    fstate.deadline = time.time() + FLASH_DURATION_SEC
                last_val = val
        time.sleep(0.1)

def handle_swipes(ds: pydualsense, fstate: FlashState):
    last_x = None
    while True:
        if ds.touchpad.touch1_active:
            current_x = ds.touchpad.touch1_x
            if last_x is not None:
                if current_x < last_x:
                    with fstate.lock:
                        fstate.active = False
                    ds.light.setColorI(0, 0, 255)
                    print("👈 Swipe left: Stealth (blue)")
                elif current_x > last_x:
                    with fstate.lock:
                        fstate.active = False
                    ds.light.setColorI(255, 0, 0)
                    print("👉 Swipe right: Alert (red)")
            last_x = current_x
        time.sleep(0.05)

def main():
    ds = pydualsense()
    try:
        ds.init()
        print("🎮 SnakeSense running. Swipe left = blue, right = red. Auto-flash on alerts.")
        fstate = FlashState()
        threading.Thread(target=flasher, args=(ds, fstate), daemon=True).start()
        threading.Thread(target=monitor_alerts, args=(ds, fstate), daemon=True).start()
        threading.Thread(target=handle_swipes, args=(ds, fstate), daemon=True).start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        ds.close()

if __name__ == "__main__":
    main()
