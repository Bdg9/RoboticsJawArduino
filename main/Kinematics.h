#ifndef KINEMATICS_H
#define KINEMATICS_H

#include "Config.h"
#include "Arduino.h"

struct Pose { float x, y, z; float roll, pitch, yaw; };

class Kinematics {
public:
    // void inverse(const Pose& pose, float lengths[6]);
    void inverse(const Pose& pose, float lengths[NUM_ACTUATORS], bool absolute = false) const;
    void rotationMatrix(float roll, float pitch, float yaw, float R[3][3]);
    Kinematics();
    void setRotationCenter(float cx, float cy, float cz);
    void setHomePose(const Pose& p);
    Pose getHomePose() const { return homePose; }
    void getRotationCenter(float& cx, float& cy, float& cz) const {
        cx = rotationCenter[0];
        cy = rotationCenter[1];
        cz = rotationCenter[2];
   }
private:
    float rotationCenter[3]; // Center of rotation (x, y, z)
    Pose homePose; // Home pose of the platform
};

#endif // KINEMATICS_H