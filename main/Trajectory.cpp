#include "Trajectory.h"

template <typename T>
T clamp(const T& value, const T& min, const T& max) {
    if (value < min) {
        Serial.print("Warning: Value ");
        Serial.print(value);
        Serial.print(" is below minimum ");
        Serial.println(min);
        return min;
    } else if (value > max) {
        Serial.print("Warning: Value ");
        Serial.print(value);
        Serial.print(" is above maximum ");
        Serial.println(max);
        return max;
    }
    return value;
}

Trajectory::Trajectory() : count(0) {}

bool Trajectory::addWaypoint(const Pose& pose, unsigned long time) {
    // Check if the pose is within the constraints
    if( pose.x < MIN_X || pose.x > MAX_X ||
       pose.y < MIN_Y || pose.y > MAX_Y ||
       pose.z < MIN_Z || pose.z > MAX_Z ||
       pose.roll < MIN_ROLL || pose.roll > MAX_ROLL ||
       pose.pitch < MIN_PITCH || pose.pitch > MAX_PITCH ||
       pose.yaw < MIN_YAW || pose.yaw > MAX_YAW) {
        Serial.println("Error: Pose out of bounds.");
        return false;
    }else if(count > 0 && time <= points[count-1].time) {
        Serial.println("Error: Time must be greater than the last waypoint.");
        return false;
    }else if(count >= MAX_POINTS) {
        Serial.println("Error: Maximum number of waypoints reached.");
        return false;
    }else if(count < MAX_POINTS) points[count++] = {pose, time}; // Add the waypoint if all checks pass
    return true;
}

Pose Trajectory::getPose(unsigned long currentTime) {
    if(count == 0) return {0,0,0,0,0,0};
    if(currentTime <= points[0].time) return points[0].pose;
    for(int i = 1; i < count; i++) {
        if(currentTime < points[i].time) {
            float t = float(currentTime - points[i-1].time) / (points[i].time - points[i-1].time);
            Pose a = points[i-1].pose, b = points[i].pose;
            Pose interpolatedPose = {
                a.x + t * (b.x - a.x),
                a.y + t * (b.y - a.y),
                a.z + t * (b.z - a.z),
                a.roll + t * (b.roll - a.roll),
                a.pitch + t * (b.pitch - a.pitch),
                a.yaw + t * (b.yaw - a.yaw)
            };
            // Clamp the interpolated pose to the defined limits
            interpolatedPose.x = clamp(interpolatedPose.x, MIN_X, MAX_X);
            interpolatedPose.y = clamp(interpolatedPose.y, MIN_Y, MAX_Y);
            interpolatedPose.z = clamp(interpolatedPose.z, MIN_Z, MAX_Z);
            interpolatedPose.roll = clamp(interpolatedPose.roll, MIN_ROLL, MAX_ROLL);
            interpolatedPose.pitch = clamp(interpolatedPose.pitch, MIN_PITCH, MAX_PITCH);
            interpolatedPose.yaw = clamp(interpolatedPose.yaw, MIN_YAW, MAX_YAW);
            interpolatedPose.y = clamp(interpolatedPose.y, MIN_Y, MAX_Y);
            interpolatedPose.z = clamp(interpolatedPose.z, MIN_Z, MAX_Z);
            interpolatedPose.roll = clamp(interpolatedPose.roll, MIN_ROLL, MAX_ROLL);
            interpolatedPose.pitch = clamp(interpolatedPose.pitch, MIN_PITCH, MAX_PITCH);
            interpolatedPose.yaw = clamp(interpolatedPose.yaw, MIN_YAW, MAX_YAW);

            return interpolatedPose;
        }
    }
    return points[count-1].pose;
}