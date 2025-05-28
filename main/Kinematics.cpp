#include "Kinematics.h"
#include <math.h>

// void Kinematics::inverse(const Pose& pose, float lengths[6]) {
//     float x = pose.x, y = pose.y, z = pose.z;
//     float cr = cos(pose.roll), sr = sin(pose.roll);
//     float cp = cos(pose.pitch), sp = sin(pose.pitch);
//     float cy = cos(pose.yaw), sy = sin(pose.yaw);
//     float R[3][3] = {
//         {cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr},
//         {sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr},
//         {-sp,   cp*sr,            cp*cr}
//     };
//     for(int i = 0; i < 6; i++) {
//         float px = PLATFORM_JOINTS[i][0], py = PLATFORM_JOINTS[i][1], pz = PLATFORM_JOINTS[i][2];
//         float wx = R[0][0]*px + R[0][1]*py + R[0][2]*pz + x;
//         float wy = R[1][0]*px + R[1][1]*py + R[1][2]*pz + y;
//         float wz = R[2][0]*px + R[2][1]*py + R[2][2]*pz + z;
//         float bx = BASE_JOINTS[i][0], by = BASE_JOINTS[i][1], bz = BASE_JOINTS[i][2];
//         lengths[i] = sqrt((wx - bx)*(wx - bx) + (wy - by)*(wy - by) + (wz - bz)*(wz - bz));
//     }
// }


// === Helper – build column‑major rotation matrix = Rz(yaw) * Ry(pitch) * Rx(roll)
void Kinematics::rotationMatrix(float roll, float pitch, float yaw, float R[3][3])
{
    float cr = cosf(roll),   sr = sinf(roll);
    float cp = cosf(pitch),  sp = sinf(pitch);
    float cy = cosf(yaw),    sy = sinf(yaw);

    R[0][0] =  cy*cp;            R[0][1] = cy*sp*sr - sy*cr;  R[0][2] = cy*sp*cr + sy*sr;
    R[1][0] =  sy*cp;            R[1][1] = sy*sp*sr + cy*cr;  R[1][2] = sy*sp*cr - cy*sr;
    R[2][0] = -sp;               R[2][1] = cp*sr;             R[2][2] = cp*cr;
}

// === Constructor ============================================================
Kinematics::Kinematics()
{
    // Default: rotation centre at platform origin & robot home pose = identity.
    rotationCenter[0] = rotationCenter[1] = rotationCenter[2] = 0.0f;
    homePose = {0,0,0, 0,0,0};
}

// === Public setters =========================================================
void Kinematics::setRotationCenter(float cx, float cy, float cz)
{
    rotationCenter[0] = cx;
    rotationCenter[1] = cy;
    rotationCenter[2] = cz;
}

void Kinematics::setHomePose(const Pose& p)
{
    homePose = p;
}

// === Inverse kinematics =====================================================
// pose → incremental pose *about the user‑defined centre* relative to the home pose.
// lengths → six actuator lengths (mm)
void Kinematics::inverse(const Pose& pose, float lengths[NUM_ACTUATORS]) const
{
    // --------------------------------------------------------------------
    // 1) Compose orientation (home ⊕ incremental)
    //    For small angles you can safely add Roll/Pitch/Yaw. For larger
    //    angles replace this section by proper matrix multiplication.
    // --------------------------------------------------------------------
    const float roll  = homePose.roll  + pose.roll;
    const float pitch = homePose.pitch + pose.pitch;
    const float yaw   = homePose.yaw   + pose.yaw;

    float R[3][3];
    rotationMatrix(roll, pitch, yaw, R);

    // --------------------------------------------------------------------
    // 2) Compose translation (home + incremental)
    //    All translations are expressed in the platform coordinate frame.
    // --------------------------------------------------------------------
    const float x = homePose.x + pose.x;
    const float y = homePose.y + pose.y;
    const float z = homePose.z + pose.z;

    // Local alias for rotation centre (gnathion).
    const float cx = rotationCenter[0];
    const float cy = rotationCenter[1];
    const float cz = rotationCenter[2];

    // --------------------------------------------------------------------
    // 3) Forward transform each platform joint and measure distance to its
    //    corresponding base joint.
    // --------------------------------------------------------------------
    for (int i = 0; i < NUM_ACTUATORS; ++i) {
        // Platform joint coordinates (local platform frame)
        float px = PLATFORM_JOINTS[i][0];
        float py = PLATFORM_JOINTS[i][1];
        float pz = PLATFORM_JOINTS[i][2];

        // Rotate *about the user‑defined centre* and translate.
        float wx = R[0][0]*(px - cx) + R[0][1]*(py - cy) + R[0][2]*(pz - cz) + x + cx;
        float wy = R[1][0]*(px - cx) + R[1][1]*(py - cy) + R[1][2]*(pz - cz) + y + cy;
        float wz = R[2][0]*(px - cx) + R[2][1]*(py - cy) + R[2][2]*(pz - cz) + z + cz;

        // Base joint coordinates (world frame)
        float bx = BASE_JOINTS[i][0];
        float by = BASE_JOINTS[i][1];
        float bz = BASE_JOINTS[i][2];

        float dx = wx - bx;
        float dy = wy - by;
        float dz = wz - bz;
        lengths[i] = sqrtf(dx*dx + dy*dy + dz*dz);
    }
}
