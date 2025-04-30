import cv2
import time
import os
import shutil
import multiprocessing
from dataclasses import dataclass
import pynmea2

@dataclass
class Config:
    TEMP_VIDEO_PATH: str = '/tmp/output.mp4'
    GPS_DATA_PATH: str = '/tmp/gps_data.txt'
    VIDEO_FOURCC: str = 'mp4v'
    FRAME_RATE: int = 20
    RESOLUTION: Tuple[int, int] = (640, 480)
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_SCALE: float = 0.5
    FONT_COLOR: Tuple[int, int, int] = (0, 255, 0)
    FONT_THICKNESS: int = 1

class VideoRecorder:
    @staticmethod
    def calculate_fps(frame_count: int, prev_time: float) -> Tuple[float, int, float]:
        curr_time = time.time()
        elapsed = curr_time - prev_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        return fps, 0, curr_time

    @staticmethod
    def add_text_to_frame(frame, text: str) -> None:
        for i, line in enumerate(text.split('\n')):
            y = frame.shape[0] - 40 + i * 20
            cv2.putText(frame, line, (10, y), 
                        Config.FONT, Config.FONT_SCALE, 
                        Config.FONT_COLOR, Config.FONT_THICKNESS, 
                        cv2.LINE_AA)

    @staticmethod
    def get_gps_data() -> Tuple[float, float]:
        try:
            with open(Config.GPS_DATA_PATH, 'r') as file:
                for line in file:
                    if line.startswith('$GNRMC'):
                        try:
                            msg = pynmea2.parse(line)
                            if msg.is_valid:
                                lat = float(msg.lat[:2]) + float(msg.lat[2:])/60
                                lng = float(msg.lon[:3]) + float(msg.lon[3:])/60
                                if msg.lat_dir == 'S':
                                    lat *= -1
                                if msg.lon_dir == 'W':
                                    lng *= -1
                                return (lat, lng)
                        except:
                            pass
        except:
            pass
        return (0.0, 0.0)

    @staticmethod
    def record_video(stop_event, gps_data_queue, command_queue):
        print("Video recorder started...")
        
        while not stop_event.is_set():
            # Wait for recording command
            if command_queue.empty():
                time.sleep(0.1)
                continue
                
            cmd = command_queue.get()
            if cmd[0] != "RECORD":
                continue
                
            video_time, usb_path = cmd[1], cmd[2]
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Error: Could not open video device")
                continue

            out = cv2.VideoWriter(Config.TEMP_VIDEO_PATH, 
                                cv2.VideoWriter_fourcc(*Config.VIDEO_FOURCC),
                                Config.FRAME_RATE, 
                                Config.RESOLUTION)

            start_time = time.time()
            frame_count, prev_time, fps = 0, start_time, 0

            print(f"\nRecording started for {video_time} minutes...")
            while (time.time() - start_time) < video_time * 60 and not stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                gps_data = VideoRecorder.get_gps_data()
                gps_data_queue.put(gps_data)

                fps, frame_count, prev_time = VideoRecorder.calculate_fps(
                    frame_count, prev_time) if (time.time() - prev_time) > 1.0 else (fps, frame_count, prev_time)

                overlay_text = f"FPS: {fps:.2f}\nLat: {gps_data[0]:.6f}, Lng: {gps_data[1]:.6f}"
                VideoRecorder.add_text_to_frame(frame, overlay_text)
                out.write(frame)

                remaining = (video_time * 60) - (time.time() - start_time)
                mins, secs = divmod(int(remaining), 60)
                print(f"\rRecording time remaining: {mins:02d}:{secs:02d}", end='')

            cap.release()
            out.release()
            print("\nVideo recording finished")

            # Transfer video
            try:
                usb_video_path = os.path.join(usb_path, 'output.mp4')
                shutil.move(Config.TEMP_VIDEO_PATH, usb_video_path)
                print(f"Video transferred to USB at {usb_video_path}")
            except Exception as e:
                print(f"Error transferring video: {e}")

            command_queue.put("DONE")

        print("Video recorder stopped.")

if __name__ == "__main__":
    # For testing
    e = multiprocessing.Event()
    gq = multiprocessing.Queue()
    cq = multiprocessing.Queue()
    VideoRecorder.record_video(e, gq, cq)