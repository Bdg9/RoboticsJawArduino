#include <Arduino.h>
#include "StewartPlatform.h"
#include "Trajectory.h"
#include "Utils.h"

StewartPlatform platform;
Trajectory trajectory;

void setup() {
    Serial.begin(9600);
    platform.begin();
    if (!platform.calibrate(true)) {
        Serial.println("Calibration failed. Stopping execution.");
        while (true) {
            // Halt execution
        }
    }

    Pose p0 = {0,0,0,0,0,0};
    Pose p1 = {0,0,50,0,0,0};
    // Pose p2 = {0,0,50,0,0,10};
    // Pose p3 = {0,0,50,0,0,-10};
    // Pose p4 = {0,0,50,0,10,0};
    // Pose p5 = {0,0,50,0,-10,0};
    // Pose p6 = {0,0,50,5,0,0};
    // Pose p7 = {0,0,50,-20,0,0};
    trajectory.addWaypoint(p0);
    trajectory.addWaypoint(p1);
    trajectory.addWaypoint(p1);
    trajectory.addWaypoint(p1);
    trajectory.addWaypoint(p1);
    trajectory.addWaypoint(p1);
    trajectory.addWaypoint(p1);
    trajectory.addWaypoint(p1);
    trajectory.addWaypoint(p0);
    trajectory.printPoints();
}

void loop() {
    //init time
    static unsigned long init_time = millis();
    static unsigned long lastUpdate = 0;
    unsigned long now = millis() - init_time;
    if(now - lastUpdate >= PLATFORM_UPDATE_INTERVAL) {
        lastUpdate = now;
        Pose target = trajectory.getPose(now);
        trajectory.printPose(target);
        platform.moveToPose(target);
        if(!platform.update()) {
            Serial.println("Error: Failed updating platform. Stoppping execution.");
            platform.stop();
            while (true) {
                    //Halt execution
             }   
        }
    }
}