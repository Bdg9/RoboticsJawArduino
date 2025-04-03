#ifndef KINEMATICS_H
#define KINEMATICS_H

#include "Config.h"
#include "Arduino.h"

struct Pose { float x, y, z; float roll, pitch, yaw; };

class Kinematics {
public:
    static void inverse(const Pose& pose, float lengths[6]);
};

#endif // KINEMATICS_H