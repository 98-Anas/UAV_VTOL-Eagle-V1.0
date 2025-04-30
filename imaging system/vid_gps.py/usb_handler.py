import os
import time
import multiprocessing
from dataclasses import dataclass

@dataclass
class Config:
    USB_MOUNT_POINT: str = '/media/zonzo'
    USB_SEARCH_TIMEOUT: int = 3  # Minutes

class USBHandler:
    @staticmethod
    def find_usb_drive() -> str:
        try:
            if not os.path.exists(Config.USB_MOUNT_POINT):
                return ""
                
            for entry in os.listdir(Config.USB_MOUNT_POINT):
                full_path = os.path.join(Config.USB_MOUNT_POINT, entry)
                if os.path.ismount(full_path):
                    return full_path
        except Exception:
            return ""
        return ""

    @staticmethod
    def monitor_usb(stop_event, usb_path_queue):
        print("USB monitor started...")
        start_time = time.time()
        timeout = Config.USB_SEARCH_TIMEOUT * 60
        
        while not stop_event.is_set():
            # Check for USB
            usb_path = USBHandler.find_usb_drive()
            
            if usb_path:
                usb_path_queue.put(usb_path)
                # Continuous monitoring while USB is present
                while not stop_event.is_set():
                    if not USBHandler.find_usb_drive():
                        usb_path_queue.put("REMOVED")
                        break
                    time.sleep(1)
                break
            elif (time.time() - start_time) >= timeout:
                usb_path_queue.put("NOT_FOUND")
                break
            
            # Show countdown
            remaining = max(0, timeout - (time.time() - start_time))
            mins, secs = divmod(int(remaining), 60)
            print(f"\rWaiting for USB: {mins:02d}:{secs:02d}", end='')
            time.sleep(1)
        
        print("\nUSB monitor stopped.")

if __name__ == "__main__":
    # For testing
    q = multiprocessing.Queue()
    e = multiprocessing.Event()
    USBHandler.monitor_usb(e, q)