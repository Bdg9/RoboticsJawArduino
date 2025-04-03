#include <Arduino.h>
#include "StewartPlatform.h"
#include "Trajectory.h"

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
    trajectory.addWaypoint(p0, 0);
    trajectory.addWaypoint(p1, 5000);
}

void loop() {
    // static unsigned long lastUpdate = 0;
    // unsigned long now = millis();
    // if(now - lastUpdate >= PLATFORM_UPDATE_INTERVAL) {
    //     lastUpdate = now;
    //     Pose target = trajectory.getPose(now);
    //     platform.moveToPose(target);
    //     platform.update();
    // }
}