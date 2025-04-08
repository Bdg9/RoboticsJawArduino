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

    Pose p0 = {0,0,Z0,0,0,0};
    Pose p1 = {0,0,Z0+50,0,0,0};
    Pose p2 = {0,0,Z0+50,0,0,degrees2rad(10)};
    Pose p3 = {0,0,Z0+50,0,0,degrees2rad(-10)};
    Pose p4 = {0,0,Z0+50,0,degrees2rad(10),0};
    Pose p5 = {0,0,Z0+50,0,degrees2rad(-10),0};
    Pose p6 = {0,0,Z0+50,degrees2rad(10),0,0};
    Pose p7 = {0,0,Z0+50,degrees2rad(-5),0,0};
    trajectory.addWaypoint(p0, 0);
    trajectory.addWaypoint(p1, 3000);
    trajectory.addWaypoint(p2,6000);
    trajectory.addWaypoint(p3, 9000);
    trajectory.addWaypoint(p4, 12000);
    trajectory.addWaypoint(p5, 15000);
    trajectory.addWaypoint(p6, 18000);
    trajectory.addWaypoint(p7, 21000);
    trajectory.addWaypoint(p0, 24000);
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