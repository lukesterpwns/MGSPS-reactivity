from pydualsense import pydualsense
import time

def main():
    ds = pydualsense()
    try:
        ds.init()
        print("🎮 DualSense connected. Swipe left for Stealth (blue), swipe right for Alert (red).")
        
        last_x = None  # Store last x position of touch
        while True:
            if ds.touchpad.touch1_active:
                current_x = ds.touchpad.touch1_x
                if last_x is not None:
                    if current_x < last_x:
                        print("👈 Swipe left detected — Stealth Mode (blue)")
                        ds.light.setColorI(0, 0, 255)  # Blue
                    elif current_x > last_x:
                        print("👉 Swipe right detected — Alert Mode (red)")
                        ds.light.setColorI(255, 0, 0)  # Red
                last_x = current_x
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        ds.close()

if __name__ == "__main__":
    main()
