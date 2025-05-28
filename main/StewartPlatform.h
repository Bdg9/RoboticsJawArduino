#ifndef STEWART_PLATFORM_H
#define STEWART_PLATFORM_H

#include "Actuator.h"
#include "Kinematics.h"

class StewartPlatform {
public:
    StewartPlatform();
    void begin();
    void moveToPose(const Pose& pose);
    void stop();
    bool update();
    bool calibrateActuators(bool fullCalibration, bool debug=false);
private:
    Actuator* actuators[6];
    float targetLengths[6];
    Kinematics kin;
};

#endif // STEWART_PLATFORM_H