#include <Arduino.h>
#include "RobotController.h"
#include "Utils.h"

RobotController robotController;

void setup() {
    Serial.begin(9600);

    // Initialize SD card
    if (!SD.begin(SD_CS)) {
        Serial.println("Error: SD card initialization failed! Stopping execution.");
        while (true) {
            // Halt execution
        }
    }

    if(!robotController.begin()) {
        Serial.println("Error: RobotController initialization failed. Stopping execution.");
        while (true) {
            // Halt execution
        }
    }

}

void loop() {
    // Handle commands sent via Serial by gui.
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        if (command.equalsIgnoreCase("start")) {
            Serial.println("Starting robot.");
            robotController.setState(RobotState::MOVING);
            return;
        }else if (command.equalsIgnoreCase("stop")) {
            Serial.println("Stopping robot.");
            robotController.setState(RobotState::STOP);
            return;
        }else if (command.equalsIgnoreCase("calibrate")) {
            Serial.println("Calibration state");
            robotController.setState(RobotState::CALIBRATING);
            return;
        }else if (command.equalsIgnoreCase("list_csv_files")) {
            listCSVFiles();
            return;
        }else if (command.startsWith("trajectory:")) {
            // Remove "trajectory:" and get the remaining part as filename.
            String filename = command.substring(11);
            filename.trim();
            Serial.print("Loading trajectory from file: ");
            Serial.println(filename);
            robotController.setTrajectoryFileName(filename);
            return;
        }else if (command.startsWith("set position:")) {
            // Parse the command to set a specific position
            String params = command.substring(13);
            params.trim();
            float x, y, z;
            if (sscanf(params.c_str(), "%f,%f,%f", &x, &y, &z) == 3) {
                // Update the global target pose.
                robotController.setCalibrationTargetPose({x, y, z, 0, 0, 0});
                Serial.println("New target position received.");
            } else {
                Serial.print("Error: Invalid parameters for set position. Message received: ");
                Serial.println(command);
            }
            return;
        }else if (command.startsWith("set origin:")) {
            // Parse the command to set a new origin
            String params = command.substring(11);
            params.trim();
            float x, y, z;
            if (sscanf(params.c_str(), "%f,%f,%f", &x, &y, &z) == 3) {
                robotController.setPlatformHomePose({x, y, z, 0, 0, 0});
                Serial.print("Origin set to: ");
                Serial.print(x); Serial.print(", ");
                Serial.print(y); Serial.print(", ");
                Serial.println(z);
            } else {
                Serial.print("Error: Invalid parameters for set origin. Message received: ");
                Serial.println(command);
            }
            return;
        } else {
            Serial.println("Unknown command. Available commands: start, stop, calibrate, list_csv_files, trajectory:<filename>, set position:<x,y,z>, set origin:<x,y,z>");
        }
    }

    robotController.update();
}