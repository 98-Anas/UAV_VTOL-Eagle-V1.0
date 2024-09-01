import cv2
import time
import multiprocessing
import os
import signal
import subprocess
import shutil

# Set the duration of the recording in minutes
record_duration = 0.1  # Change this value as needed
usb_mount_point = '/media/zonzo/02B5-F5D41'  # Change this to your actual USB mount point

def read_gps(pipe, stop_event):
    import pynmea2

    def convert_to_decimal(degree_minute, direction):
        if not degree_minute or not direction:
            return None
        if direction in ['N', 'S']:
            degree = int(degree_minute[:2])
            minute = float(degree_minute[2:])
        else:
            degree = int(degree_minute[:3])
            minute = float(degree_minute[3:])
        decimal = degree + (minute / 60)
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal

    buffer = ""

    while not stop_event.is_set():
        try:
            with open('/tmp/gps_data.txt', 'r', encoding='ascii', errors='replace') as file:
                for line in file:
                    buffer += line
                    if "\n" in buffer:
                        lines = buffer.split("\n")
                        buffer = lines[-1]
                        for full_line in lines[:-1]:
                            if full_line.startswith('$GNRMC'):
                                try:
                                    newmsg = pynmea2.parse(full_line)
                                    if newmsg.is_valid:
                                        lat = convert_to_decimal(newmsg.lat, newmsg.lat_dir)
                                        lng = convert_to_decimal(newmsg.lon, newmsg.lon_dir)

                                        if lat is not None and lng is not None:
                                            pipe.send((lat, lng))
                                except pynmea2.ParseError as e:
                                    print(f"Parse error: {e}")
                                    print(f"Full line: {full_line}")
                                except Exception as e:
                                    print(f"Error: {e}")
                                    print(f"Full line: {full_line}")
        except FileNotFoundError:
            print("Waiting for GPS data...")
            time.sleep(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)

def record_video(pipe, stop_event):
    # Video capture setup
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_video_path = '/tmp/output.mp4'
    out = cv2.VideoWriter(temp_video_path, fourcc, 20.0, (640, 480))

    start_time = time.time()
    gps_data = (0.0, 0.0)
    
    print("Video recording started...")
    prev_time = start_time
    frame_count = 0
    fps = 0

    while (time.time() - start_time) < record_duration * 60:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        curr_time = time.time()
        elapsed_time = curr_time - prev_time
        if elapsed_time > 1.0:
            fps = frame_count / elapsed_time
            frame_count = 0
            prev_time = curr_time

        if pipe.poll():
            gps_data = pipe.recv()

        lat, lng = gps_data
        text = f"FPS: {fps:.2f}\nLat: {lat:.6f}, Lng: {lng:.6f}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        for i, line in enumerate(text.split('\n')):
            y = frame.shape[0] - 40 + i * 20
            cv2.putText(frame, line, (10, y), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

        out.write(frame)

    cap.release()
    out.release()
    stop_event.set()
    print("Video recording finished and saved as output.mp4")

    # Transfer the video to the USB storage
    if os.path.ismount(usb_mount_point):
        usb_video_path = os.path.join(usb_mount_point, 'output.mp4')
        shutil.move(temp_video_path, usb_video_path)
        print(f"Video transferred to USB storage at {usb_video_path}. You can safely remove the USB drive.")
    else:
        print("USB storage not found. Video not transferred.")

def terminate_script(script_name):
    result = subprocess.run(['pgrep', '-f', script_name], stdout=subprocess.PIPE)
    pids = result.stdout.decode().split()
    for pid in pids:
        os.kill(int(pid), signal.SIGTERM)
    print(f"Terminated {script_name} and its running processes")

if __name__ == "__main__":
    parent_conn, child_conn = multiprocessing.Pipe()
    stop_event = multiprocessing.Event()

    gps_process = multiprocessing.Process(target=read_gps, args=(child_conn, stop_event))
    video_process = multiprocessing.Process(target=record_video, args=(parent_conn, stop_event))

    gps_process.start()
    video_process.start()

    video_process.join()
    stop_event.set()  # Ensure the stop event is set
    gps_process.join()

    terminate_script('sys_run.sh')

    print("All processes have finished. Returning to terminal.")
