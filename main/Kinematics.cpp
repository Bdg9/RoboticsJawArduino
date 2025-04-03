#include "Kinematics.h"
#include <math.h>

void Kinematics::inverse(const Pose& pose, float lengths[6]) {
    float x = pose.x, y = pose.y, z = pose.z;
    float cr = cos(pose.roll), sr = sin(pose.roll);
    float cp = cos(pose.pitch), sp = sin(pose.pitch);
    float cy = cos(pose.yaw), sy = sin(pose.yaw);
    float R[3][3] = {
        {cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr},
        {sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr},
        {-sp,   cp*sr,            cp*cr}
    };
    for(int i = 0; i < 6; i++) {
        float px = PLATFORM_JOINTS[i][0], py = PLATFORM_JOINTS[i][1], pz = PLATFORM_JOINTS[i][2];
        float wx = R[0][0]*px + R[0][1]*py + R[0][2]*pz + x;
        float wy = R[1][0]*px + R[1][1]*py + R[1][2]*pz + y;
        float wz = R[2][0]*px + R[2][1]*py + R[2][2]*pz + z;
        float bx = BASE_JOINTS[i][0], by = BASE_JOINTS[i][1], bz = BASE_JOINTS[i][2];
        lengths[i] = sqrt((wx - bx)*(wx - bx) + (wy - by)*(wy - by) + (wz - bz)*(wz - bz));
    }
}