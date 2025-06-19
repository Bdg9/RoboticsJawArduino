# RoboticsJawArduino

This repository contains all the code used for my master thesis project at CREATE Lab, EPFL. 

## Folder structure
- `data_processing/`: Code for processing the motion capture data into a .csv trajectory to be replayed by the robotic jaw.
- `gui/`: Python code for the GUI that allows users to control the robotic jaw.
- `main/`: Arduino code for controlling the robotic jaw.
- `plots_generation/`: Code to generate the graphs for the thesis report.
- `report/`: Latex code to generate the thesis report.
- `Results/`: Folder in which the results of the tests on the robot are stored.
- `tests/`: Folder with different tests used to develop the robotic jaw.
- `video_pic_real_robot/`: Demo video of the robotic jaw in action and pictures of the real robot.

## How to run it
1. Clone the repository
2. Install Arduino IDE and the required libraries for the main code
3. Upload the code in `main/` to the Teensy 4.1 
4. Open the Python GUI in `gui/` to control the robotic jaw ('jaw_gui.py')
5. Now you can control the robot using the GUI

## Add a new trajectory
1. Record a new trajectory using the motion capture system
2. Process the data using the code `data_processing/motion_capture_to_traj.py` to generate a .csv file
3. Visualize the trajectory using `data_processing/visualize_traj.py` and find the portion you want to replay
4. Extract the portion of the trajectory you want to replay using `data_processing/extract_cycle.py`
5. Upload the new trajectory to the Teensy 4.1 built-in SD card in the `robotics_jaw/` folder
6. Open the GUI in `gui/` and select the new trajectory from the dropdown menu
7. Calibrate the robot home position using the GUI
8. Press start to replay the trajectory

## Demo Short
[![Watch on YouTube](https://img.youtube.com/shorts/_uW6wkvUZ1g/hqdefault.jpg)](https://www.youtube.com/shorts/_uW6wkvUZ1g)




