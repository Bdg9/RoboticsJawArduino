#include <Arduino.h>
#include "StewartPlatform.h"
#include "Trajectory.h"
#include "Utils.h"

StewartPlatform platform;
Trajectory trajectory;

//TODO: make calib into state machine
// Define a global variable for the target pose.
Pose currentTarget = {0, 0, Z0+5, 0, 0, 0};

void setup() {
    Serial.begin(9600);

    // Initialize SD card
    if (!SD.begin(SD_CS)) {
        Serial.println("Error: SD card initialization failed!");
    }

    platform.begin();
    if (!platform.calibrateActuators(false, true)) {
        Serial.println("Error: Calibration failed. Stopping execution.");
        while (true) {
            // Halt execution
        }
    }

    if (!trajectory.loadFromCSV("test_trajectory.csv")) {
        Serial.println("Error: Failed to load trajectory from CSV.");
        // Halt execution
        while (true) {
            // Halt execution
        }
    }

    trajectory.printPoints();
}

void loop() {
    if (Serial.available()) {
        //if command is start
        String command = Serial.readStringUntil('\n');
        command.trim();
        if (command.equalsIgnoreCase("start")) {
            Serial.println("Starting file reading...");
            return;
        }else if (command.equalsIgnoreCase("stop")) {
            Serial.println("Stopping file reading...");
            return;
        }else if (command.equalsIgnoreCase("calibrate")) {
            Serial.println("calibrating...");
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
            if (!trajectory.loadFromCSV(filename)) {
                Serial.println("Error: Failed to load trajectory from CSV.");
            } else {
                Serial.println("Trajectory loaded successfully:");
                trajectory.printPoints();
            }
            return;
        }else if (command.startsWith("set position:")) {
            // Parse the command to set a specific position
            String params = command.substring(13);
            params.trim();
            float x, y, z;
            if (sscanf(params.c_str(), "%f,%f,%f", &x, &y, &z) == 3) {
                // Update the global target pose.
                currentTarget = {x, y, z, 0, 0, 0};
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
                platform.setHomePose({x, y, z, 0, 0, 0});
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

    static unsigned long init_time = millis();
    static unsigned long lastUpdate = 0;
    unsigned long now = millis() - init_time;
    if(now - lastUpdate >= PLATFORM_UPDATE_INTERVAL) {
        lastUpdate = now;
        //trajectory.printPose(currentTarget);
        platform.moveToPose(currentTarget);
        if(!platform.update(false)) {
            Serial.println("Error: Failed updating platform. Stoppping execution.");
            platform.stop();
            while (true) {
                    //Halt execution
             }   
        }
    }

    // //init time
    // static unsigned long init_time = millis();
    // static unsigned long lastUpdate = 0;
    // unsigned long now = millis() - init_time;
    // if(now - lastUpdate >= PLATFORM_UPDATE_INTERVAL) {
    //     lastUpdate = now;
    //     Pose target = trajectory.getPose(now);
    //     trajectory.printPose(target);
    //     platform.moveToPose(target);
    //     if(!platform.update()) {
    //         Serial.println("Error: Failed updating platform. Stoppping execution.");
    //         platform.stop();
    //         while (true) {
    //                 //Halt execution
    //          }   
    //     }
    // }
}