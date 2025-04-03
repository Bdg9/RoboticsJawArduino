#ifndef TRAJECTORY_H
#define TRAJECTORY_H

#include "Kinematics.h"

class Trajectory {
public:
    Trajectory();
    void addWaypoint(const Pose& pose, unsigned long time);
    Pose getPose(unsigned long currentTime);
private:
    static const int MAX_POINTS = 10;
    struct Waypoint { Pose pose; unsigned long time; } points[MAX_POINTS];
    int count;
};

#endif // TRAJECTORY_H