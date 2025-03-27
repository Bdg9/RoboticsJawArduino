#include "Trajectory.h"

Trajectory::Trajectory() : count(0) {}

void Trajectory::addWaypoint(const Pose& pose, unsigned long time) {
    if(count < MAX_POINTS) points[count++] = {pose, time};
}

Pose Trajectory::getPose(unsigned long currentTime) {
    if(count == 0) return {0,0,0,0,0,0};
    if(currentTime <= points[0].time) return points[0].pose;
    for(int i = 1; i < count; i++) {
        if(currentTime < points[i].time) {
            float t = float(currentTime - points[i-1].time) / (points[i].time - points[i-1].time);
            Pose a = points[i-1].pose, b = points[i].pose;
            return {a.x + t*(b.x-a.x), a.y + t*(b.y-a.y), a.z + t*(b.z-a.z), a.roll + t*(b.roll-a.roll), a.pitch + t*(b.pitch-a.pitch), a.yaw + t*(b.yaw-a.yaw)};
        }
    }
    return points[count-1].pose;
}