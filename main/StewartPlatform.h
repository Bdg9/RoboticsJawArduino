#ifndef STEWART_PLATFORM_H
#define STEWART_PLATFORM_H

#include "Actuator.h"
#include "Kinematics.h"

class StewartPlatform {
public:
    StewartPlatform();
    void begin();
    void moveToPose(const Pose& pose);
    bool update();
    bool calibrate(bool debug=false);
private:
    Actuator* actuators[6];
    float targetLengths[6];
};

#endif // STEWART_PLATFORM_H