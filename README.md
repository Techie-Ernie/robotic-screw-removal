# Nanyang Resarch Programme: NIE05C
## Developing a robotic system for automated screw extraction in e-waste recycling 

By Ernest Chan Ern Yi (HCI) and Tran Thien Tri (ASRJC)

### Description
This research details the design and
implementation of a vision-guided robotic system
for the automated extraction of screws from laptop
back panels, addressing a critical throughput
bottleneck in electronic waste (e-waste) recycling.
The hardware comprises a custom-engineered
Computer Numerical Control (CNC) plotter-style
gantry built with aluminium extrusions and
3D-printed mounts, driven by NEMA 17 stepper
motors. The system utilises a multi-stage control
architecture: a Raspberry Pi AI Camera executes
a YOLOv11n object detection model on-device for
real-time screw detection, while a Raspberry Pi 4B
serves as the central hub for coordinate
calibration and system orchestration. Detected
pixel coordinates are translated into physical
machine-space through homography mapping,
with movement commands transmitted from the
Raspberry Pi to an Arduino-based CNC shield to
drive the motors.

## Structure

### Folders

**tests/** 
- **rpi/** 
- **arduino/** 

**rpi/** contains various test scripts to test the Raspberry Pi AI Camera, serial communication, etc.

**arduino/** contains various test scripts to test motor control and serial communication.

**dataset**/

Contains the necessary scripts for generating our screw dataset, including ```generate_dataest.py``` for generating synthetic screw images and ```dataset_creation.py``` for capturing a series of images from the Raspberry Pi AI Camera for use in the dataset.

**calibration**/

Contains ```calibrate_aruco.py``` needed for camera calibration, producing a homography matrix used to map the virtual coordinates of screws into real-world coordinates to be sent as GRBL commands. 

### Standalone scripts

```gcode-sender.py```:  interactive interface to send GRBL commands directly

```grbl.py```: provides the GRBL class used in ```main.py```, which is used for system-wide control 

```imx_detect.py``` handles the detection of screws and returns the screw coordinates to ```main.py``` for it to send the corresponding GRBL command. 

```main.py```: main control script, handles screw detection, motor control and screw extraction

## Acknowledgements
We would like to express our deepest gratitude to our mentor, Dr Lim Yang Teck Kenneth, for his invaluable support and guidance throughout the course of the project.

It would be remiss if we did not thank Kwok Xin Ze Vincent, Ahmed Hazyl Hilmy and Tan Jun Hao Alan, who have provided invaluable technical expertise to guide our project. 