import multiprocessing
import time
import signal
import sys
from usb_handler import USBHandler
from video_recorder import VideoRecorder

class MainController:
    def __init__(self):
        self.usb_process = None
        self.video_process = None
        self.stop_event = multiprocessing.Event()
        self.usb_path_queue = multiprocessing.Queue()
        self.gps_data_queue = multiprocessing.Queue()
        self.command_queue = multiprocessing.Queue()

    def handle_shutdown(self, signum, frame):
        print("\nShutting down processes...")
        self.stop_event.set()
        if self.usb_process:
            self.usb_process.terminate()
        if self.video_process:
            self.video_process.terminate()
        sys.exit(0)

    def start_processes(self):
        # Start USB handler process
        self.usb_process = multiprocessing.Process(
            target=USBHandler.monitor_usb,
            args=(self.stop_event, self.usb_path_queue)
        )
        self.usb_process.start()

        # Wait for USB to be found
        usb_path = None
        try:
            while not self.stop_event.is_set():
                if not self.usb_path_queue.empty():
                    usb_path = self.usb_path_queue.get()
                    if usb_path == "NOT_FOUND":
                        print("USB not found within timeout. Terminating.")
                        self.stop_event.set()
                        break
                    elif usb_path.startswith("/"):
                        print(f"USB found at: {usb_path}")
                        break
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop_event.set()

        if self.stop_event.is_set() or not usb_path:
            return

        # Start video recorder process
        self.video_process = multiprocessing.Process(
            target=VideoRecorder.record_video,
            args=(self.stop_event, self.gps_data_queue, self.command_queue)
        )
        self.video_process.start()

        # Main control loop
        try:
            while not self.stop_event.is_set():
                self.user_interface(usb_path)
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop_event.set()

    def user_interface(self, usb_path):
        try:
            video_time = float(input("Enter recording time in minutes (or 'q' to quit): "))
            self.command_queue.put(("RECORD", video_time, usb_path))
            
            # Wait for recording to complete
            while not self.stop_event.is_set():
                if not self.command_queue.empty():
                    cmd = self.command_queue.get()
                    if cmd == "DONE":
                        break
                time.sleep(0.1)

            choice = input("Record again? (y/n): ").lower()
            if choice != 'y':
                self.stop_event.set()
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            self.stop_event.set()

if __name__ == "__main__":
    controller = MainController()
    signal.signal(signal.SIGINT, controller.handle_shutdown)
    signal.signal(signal.SIGTERM, controller.handle_shutdown)
    controller.start_processes()