# UAV_VTOL-EagleV1.0
This repo contains the first system desinged for Eagles Team' VTOL Unmanned aerial vehicle.

# UAV Imaging System

## System Block Diagram
![UAV_VTOL System Block Diagram](https://github.com/user-attachments/assets/25a8dc55-6261-436f-afd5-4b424200b546)

## System Workflow Diagram
![UAV_VTOL System WorkFlow](https://github.com/user-attachments/assets/2f61b93e-dae1-41a4-8111-218de3d76ce8)

## System Components:
1. Raspberry Pi 5 (8GB RAM)
2. 12V-24V Buck Converter (Step down to 5V 5A)
3. Samsung Evo Plus 64GB (Booting disk)
4. Logitech USB Webcam (30 FPS)
5. Ublox-NEO-M8N GPS Positioning Module
6. orange cube flight controller
7. ppm encoder
8. remote reciever
9. 9S lipo battery for thrust motor
10. 6s lipo battery for the rest of the system
11. power distribution board for hover motors
12. SIK Telemetry Radio V3

### Very Important NOTE: This system is not completed yet as it is still under testing and development.
### Special Thanks to: George, Krolus and Ahmed Alaa for their great efforts and contributions in this system.  

## Simple hover test on gazebo simulator (ROS 1 - Ubuntu 20.04)
https://github.com/user-attachments/assets/f97c25e1-082e-4965-86a0-d50519fdec1b

## For Mission Planner Configurations 
1. https://ardupilot.org/plane/docs/quadplane-support.html
2. https://ardupilot.org/plane/docs/quadplane-auto-mode.html
3. https://ardupilot.org/plane/docs/quadplane-vtol-tuning.html

## For QGround Configurations 
https://docs.px4.io/main/en/frames_vtol/

## For Simulation Tutorials
https://www.youtube.com/@IntelligentQuads/playlists

## For pymavlink tutorials
https://www.youtube.com/playlist?list=PLy9nLDKxDN68cwdt5EznyAul6R8mUSNou

## To use companion computers either for Mission Planner or QGround
1. https://ardupilot.org/dev/docs/companion-computers.html
2. https://docs.px4.io/main/en/companion_computer/pixhawk_companion.html

## To use ROS 1 or 2 (ROS2 is recommended) Mission Planner or QGround
1. https://ardupilot.org/dev/docs/ros.html
2. https://docs.px4.io/main/en/dev_setup/dev_env.html

## Recommended Discord channels for support 
1. (Droncode) https://discord.gg/dronecode 
2. (ArduPilot) https://discord.gg/svCkuxth4n 

## NU Autonomous Robotics Notion Workspace with more resources 
https://awesome-mongoose-6ca.notion.site/Autonomous-Robotics-NU-b3b0c370bd624ed4915d17acc76dab40?pvs=4

![robotics workspace](https://github.com/user-attachments/assets/023374e9-325e-4074-a878-cdb9cc16a30d)
