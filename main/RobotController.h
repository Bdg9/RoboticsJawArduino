#ifndef ROBOT_CONTROLLER_H
#define ROBOT_CONTROLLER_H

#include "StewartPlatform.h"
#include "Trajectory.h" 

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
    void setPlatformHomePose(const Pose& pose);
    void setCalibrationTargetPose(const Pose& pose);

private:
    RobotState state;
    StewartPlatform* platform;
    Trajectory trajectory; // Assuming a Trajectory class exists
    Pose calibrationTargetPose; // Target pose for calibration

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