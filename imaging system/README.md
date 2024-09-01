# UAV Imaging System
This repository contains the code and scripts used for a VTOL (Vertical Take-Off and Landing) UAV imaging system. The system is designed to record video footage with embedded GPS coordinates and FPS (frame per second), captured during the mission. The GPS data is continuously read from a GPS module and overlaid onto the video frames in real-time. The final video file, complete with GPS data, is saved to a USB storage device for easy retrieval.

## System Block Diagram
![Companion Computer (SBC)](https://github.com/user-attachments/assets/0f4466d1-82da-45e2-8a17-c8f3875cd3bc)

## System Components:
1. Raspberry Pi 5 (8GB RAM)
2. 12V-24V Buck Converter (Step down to 5V 5A)
3. Samsung Evo Plus 64GB (Booting disk)
4. Logitech USB Webcam (30 FPS)
5. Ublox-NEO-M8N GPS Positioning Module

## Overclocking and Performance
The Raspberry Pi 5 is overclocked from 2.4GHz to 2.7GHz to enhance performance. This allows the camera to reach 30 FPS by utilizing all four cores of the CPU. Additionally, the system uses a swap file on the booting disk to create virtual RAM, extending the RAM from 8GB to 16GB. This configuration supports real-time imaging and extensive data processing during runtime.

## Environment Setup
The environment is prepared using Miniforge to create a virtual environment and install the necessary libraries for OpenCV (computer vision library), TensorFlow, and Pynmea (GPS hardware library).

## System Workflow Explanation
The system involves initializing the GPS module, reading GPS data, and recording video with embedded GPS information. The main script (`sys_run.sh`) coordinates these tasks, ensuring that the processes run concurrently.

Here’s an explanation of each script and the overall workflow:

### `sys_run.sh`
This script initializes the system and starts the necessary processes.
1. The script clears the terminal and prints initialization messages.
2. It starts the `start_gps.sh` script to begin reading GPS data.
3. After a short delay, it starts the `vid_gps.py` script to begin video recording.

### `start_gps.sh`
This script continuously reads GPS data from the GPS module and writes it to a temporary file.
1. The script sets the necessary permissions for accessing the GPS module.
2. It continuously reads GPS data from `/dev/ttyAMA0` and writes it to `/tmp/gps_data.txt`.
3. The loop ensures that the script keeps running, updating the GPS data file every second.

### `vid_gps.py`
This script records video from the webcam and overlays GPS information on the video frames.
1. The `read_gps` function continuously reads GPS data from the temporary file and sends the parsed coordinates through a pipe to the `record_video` function.
2. The `record_video` function captures video from the webcam, overlays the FPS and GPS coordinates on the video frames, and saves the video to a temporary file.
3. After recording, the video is transferred to a USB storage device if it is mounted.
   - The script ensures all processes are terminated properly by checking for running processes related to the system script and terminating them. (This feature has a bug that needs to be fixed.)

## Addressing SSH Connection Loss
If the SSH connection is lost, the bash script will terminate. To solve this, you can run the script in the background using `nohup` or `tmux`.

### Using this command:
```bash
nohup ./sys_run.sh &
```

### OR

### Using this command:
1. Install TMUX if not installed:
   ```bash
   sudo apt-get install tmux -y
   ```
2. Create a new TMUX session:
   ```bash
   tmux new-session -d -s my_session './sys_run.sh'
   ```

## Steps for Preparing the System Environment
1. Flash Raspberry Pi OS (Bookworm 64-Bit: [Download](https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-64-bit)) or Ubuntu ([Download](https://ubuntu.com/raspberry-pi)).

### In Raspberry Pi 5, you can safely overclock to 2.7GHz with its active cooler. Follow these steps carefully but after the initial setup steps:
1. Open the config file:
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
2. Copy and paste the following lines to the end of this file:
   ```bash
   arm_freq=2200
   gpu_freq=750
   over_voltage=6
   ```
3. Save (`Ctrl + S`, `Ctrl + X`) and then reboot:
   ```bash
   sudo reboot
   ```

### Initial Setup Steps
You can find the initial steps (1, 2, 3, 4) in my [tutorial here](https://www.youtube.com/watch?v=cKhocaaQgyM):
1. SSH to Raspberry Pi.
2. Expand the file system.
3. Set the GPU memory to 128.
4. Create an 8GB swap file (8 x 1024 = 8192) for virtual RAM. Follow only the swap file steps from this [link](https://qengineering.eu/install%20opencv%20on%20raspberry%20pi%205.html).

### To Create a Python Virtual Environment Using Miniconda ([Download Miniconda](https://github.com/conda-forge/miniforge))
```bash
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh
sudo chmod +x Miniforge3-Linux-aarch64.sh
./Miniforge3-Linux-aarch64.sh
```
- Close and reopen the terminal, ensuring it is on the `base` environment.
- Create and activate the `vtol` environment:
   ```bash
   conda create -n vtol python=3.9.2
   conda activate vtol
   ```

### Install Required Libraries in the `vtol` Environment:
```bash
pip install opencv-python-headless numpy pynmea2 pyserial
```

## Steps for GPS Configuration ([Instructables Guide](https://www.instructables.com/Interfacing-GPS-Module-With-Raspberry-Pi/))
1. **Disable Serial Console:**
   - Ensure that the serial console is disabled to free up the UART for your script.
   - Run:
     ```bash
     sudo raspi-config
     ```
   - Navigate to Interfacing Options > Serial:
     - When prompted, select **No** for "Would you like a login shell to be accessible over serial?"
     - Select **Yes** for "Would you like the serial port hardware to be enabled?"
   - Reboot the Raspberry Pi.
