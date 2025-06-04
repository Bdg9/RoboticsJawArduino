#include "RobotController.h"
#include <Arduino.h>

// ========= Public methods implementation ===========

bool RobotController::begin() {
    platform.begin();
    // Calibrate min of the actuator at each boot
    if (!platform.calibrateActuators(false, true)) {
        Serial.println("Error: Actuator calibration failed. Stopping execution.");
        setState(RobotState::STOP);
        return false;
    }

    if (!loadTrajectoryFromFile(trajectoryFileName)) {
        Serial.println("Error: Failed to load trajectory from file.");
        setState(RobotState::STOP);
        return false;
    }

    trajectory.printPoints();
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

void RobotController::setPlatformHomePose(const Pose& pose) {
    platform.setHomePose(pose);
}

void RobotController::setCalibrationTargetPose(const Pose& pose) {
    if(state == RobotState::CALIBRATING) {
        calibrationTargetPose = pose;
    } else {
        Serial.println("Error: Platform is not in CALIBRATING state. Setting calibration target pose not possible.");
    }
}

void RobotController::setFixedInterval(unsigned long interval) {
    fixedInterval = interval;
}

// ========= Private methods implementation ===========

void RobotController::calibrate() {
    static unsigned long init_time = millis();
    static unsigned long lastUpdate = 0;
    unsigned long now = millis() - init_time;
    if(now - lastUpdate >= PLATFORM_UPDATE_INTERVAL) {
        lastUpdate = now;
        //trajectory.printPose(currentTarget);
        platform.moveToPose(calibrationTargetPose, true); // Move to target pose with absolute position kinematics
        if(!platform.update(false)) {
            Serial.println("Error: Failed updating platform. Stopping robot.");
            setState(RobotState::STOP);
        }
    }
    // update and print the force sensing data
    forceSensing.update();
    forceSensing.printForce();
}

void RobotController::move() {
    //init time
    static unsigned long lastUpdate = 0;
    unsigned long now = millis() - trajectoryInitTime;
    if(now - lastUpdate >= PLATFORM_UPDATE_INTERVAL) {
        lastUpdate = now;
        Pose target = trajectory.getPose(now);
        trajectory.printPose(target);
        platform.moveToPose(target);
        if(!platform.update()) {
            Serial.println("Error: Failed updating platform. Stoppping execution.");
            setState(RobotState::STOP); 
            return;
        }
    }
}

void RobotController::stop() {
    //load the trajectory file if filename has changed
    if(loadedTrajectoryFileName != trajectoryFileName) {        
        if (!loadTrajectoryFromFile(trajectoryFileName)) {
            Serial.println("Error: Failed to load trajectory from file.");
        } 
    }

    if(trajectory.getFixedInterval() != fixedInterval) {
        trajectory.setFixedInterval(fixedInterval);
        Serial.print("Fixed interval set to: ");
        Serial.println(fixedInterval);

        if(!trajectory.loadFromCSV(trajectoryFileName)){ // Reload trajectory with new fixed interval
            Serial.println("Error: Failed to reload trajectory with new fixed interval.");
        }else{
            loadedTrajectoryFileName = trajectoryFileName; // Update the loaded trajectory file name
        }
    }

    // If the robot is in STOP state, make platform return to home pose.
    static unsigned long init_time = millis();
    static unsigned long lastUpdate = 0;
    unsigned long now = millis() - init_time;
    if(now - lastUpdate >= PLATFORM_UPDATE_INTERVAL) {
        lastUpdate = now;
        //trajectory.printPose(platform.getHomePose());
        platform.moveToHomePose(); // Move to home pose
        if(!platform.update(false)) {
            Serial.println("Error: Failed updating platform. Stopping robot.");
            setState(RobotState::STOP); //TODO: error state ?
        }
    }
}

void RobotController::onEnterCalibrating() {
    Serial.println("Entering calibration state.");

    // Stop movement before calibration begins.
    platform.stop();
    
    // Similarly, other subsystems could be prepared for a manual calibration mode.
}

void RobotController::onEnterMoving() {
    Serial.println("Entering moving state.");
    // When moving, start the trajectory and coordinate subsystems.
    // Start tongue and saliva pumps, eyes synchronization if needed.
    trajectoryInitTime = millis(); // Record the time when moving starts
}

void RobotController::onEnterStop() {
    Serial.println("Entering stop state.");
    // Stop all subsystems.
    platform.stop();
    
    // Stop other subsystems if necessary.
}

bool RobotController::loadTrajectoryFromFile(const String& filename) {
    if (trajectory.loadFromCSV(filename)) {
        loadedTrajectoryFileName = filename; // Track the currently loaded trajectory file
        trajectory.printPoints(); // Print loaded trajectory points 
    } else {
        Serial.println("Error: Failed to load trajectory from file.");
        return false;
    }
    return true;
}