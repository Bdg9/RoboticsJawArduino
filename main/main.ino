#include <Arduino.h>
#include "StewartPlatform.h"
#include "Trajectory.h"
#include "Utils.h"

StewartPlatform platform;
Trajectory trajectory;

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