#ifndef ROBOT_CONTROLLER_H
#define ROBOT_CONTROLLER_H

#include "StewartPlatform.h"

enum class RobotState {
    CALIBRATING,
    MOVING,
    STOP
};

class RobotController {
public:
    RobotController(StewartPlatform* platform);

    // Current state getter
    RobotState getState() const;
    bool setState(RobotState newState);

    // Add additional functions to coordinate subsystems during transitions
    void update();  // For periodic updates if needed

private:
    RobotState state;
    StewartPlatform* platform;

    // State-specific methods
    void calibrate();     
    void move();    
    void stop();           

    // Helper methods for state transitions
    void onEnterCalibrating();
    void onEnterMoving();
    void onEnterStop();
};

#endif // ROBOT_CONTROLLER_H