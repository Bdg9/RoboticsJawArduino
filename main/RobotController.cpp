#include "RobotController.h"
#include <Arduino.h>

RobotController::RobotController(StewartPlatform* platform) 
    : state(RobotState::STOP), platform(platform)
{
}

void RobotController::calibrate() {
}

void RobotController::move() {
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
            // platform.stop();
            // while (true) {
            //         //Halt execution
            //  } 
            state = RobotState::STOP;  
            onEnterStop();
            return;
        }
    }

}

void RobotController::stop() {
}

RobotState RobotController::getState() const {
    return state;
}

bool RobotController::setState(RobotState newState) {
    if (newState == state) return true; // No state change

    RobotState prevState = state;
    // Check for disallowed transitions before updating the state.
    if (prevState == RobotState::MOVING && newState == RobotState::CALIBRATING) {
        Serial.println("Error: Cannot transition from MOVING to CALIBRATING.");
        return false;
    }
    if (prevState == RobotState::CALIBRATING && newState == RobotState::MOVING) {
        Serial.println("Error: Cannot transition from CALIBRATING to MOVING.");
        return false;
    }

    state = newState;
    switch (newState) {
        case RobotState::CALIBRATING:
            onEnterCalibrating();
            break;
        case RobotState::MOVING:
            onEnterMoving();
            break;
        case RobotState::STOP:
            onEnterStop();
            break;
    }
    return true;
}

void RobotController::update() {
    if(state == RobotState::MOVING) {
        move();
    }
    else if(state == RobotState::CALIBRATING) {
        calibrate();
    }
    else if(state == RobotState::STOP) {
        stop();
    }
}

void RobotController::onEnterCalibrating() {
    Serial.println("Entering calibration state.");
    // For calibration: activate the stewart platform calibration routines,
    // allow GUI commands such as arrow keys, set origin, etc.
    if(platform) {
        // Optionally, stop movement before calibration begins.
        platform->stop();
    }
    // Similarly, other subsystems could be prepared for a manual calibration mode.
}

void RobotController::onEnterMoving() {
    Serial.println("Entering moving state.");
    // When moving, start the trajectory and coordinate subsystems.
    if(platform) {
        // For example: platform->beginTrajectory(...) etc.
    }
    // Start tongue and saliva pumps, eyes synchronization if needed.
}

void RobotController::onEnterStop() {
    Serial.println("Entering stop state.");
    // Stop all subsystems.
    if(platform) {
        platform->stop();
    }
    // Stop other subsystems if necessary.
}