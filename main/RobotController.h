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
    // Current state getter
    RobotState getState() const;
    bool setState(RobotState newState);

    // Add additional functions to coordinate subsystems during transitions
    bool begin();
    void update();  // For periodic updates if needed
    void setPlatformHomePose(const Pose& pose);
    void setCalibrationTargetPose(const Pose& pose);
    void setTrajectoryFileName(const String& filename) {
        trajectoryFileName = filename;
    }
    void setFixedInterval(unsigned long interval);

private:
    RobotState state = RobotState::STOP; // Initial state
    StewartPlatform platform;
    Trajectory trajectory; // Assuming a Trajectory class exists
    Pose calibrationTargetPose = {0, 0, Z0+5, 0, 0, 0}; // Target pose for calibration
    String trajectoryFileName = "test_trajectory.csv"; // File name for trajectory
    String loadedTrajectoryFileName = ""; // Track the currently loaded trajectory file
    unsigned long trajectoryInitTime = 0; // Time when trajectory is started because we changed to MOVING state
    unsigned long fixedInterval = 100; // Default fixed interval for trajectory points in milliseconds

    // State-specific methods
    void calibrate();     
    void move();    
    void stop();           

    // Helper methods for state transitions
    void onEnterCalibrating();
    void onEnterMoving();
    void onEnterStop();
    bool loadTrajectoryFromFile(const String& filename);

};

#endif // ROBOT_CONTROLLER_H