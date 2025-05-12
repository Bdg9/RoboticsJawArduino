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

Trajectory::Trajectory(unsigned long fixedInterval) : count(0), fixedInterval(fixedInterval) {}

bool Trajectory::addWaypoint(const Pose& pose) {
    pose.x = Z0 + pose.x; // Adjust the x coordinate to the Z0 level.
    pose.roll = degrees2rad(pose.roll); // Convert roll, pitch, and yaw from degrees to radians.
    pose.pitch = degrees2rad(pose.pitch);
    pose.yaw = degrees2rad(pose.yaw);
    // Validate that the pose is within the allowed limits.
    if( pose.x < MIN_X || pose.x > MAX_X ||
        pose.y < MIN_Y || pose.y > MAX_Y ||
        pose.z < MIN_Z || pose.z > MAX_Z ||
        pose.roll < MIN_ROLL || pose.roll > MAX_ROLL ||
        pose.pitch < MIN_PITCH || pose.pitch > MAX_PITCH ||
        pose.yaw < MIN_YAW || pose.yaw > MAX_YAW) {
        Serial.println("Error: Pose out of bounds.");
        return false;
    }
    if(count >= MAX_POINTS) {
        Serial.println("Error: Maximum number of waypoints reached.");
        return false;
    }
    // Compute time using fixed interval. First waypoint at time 0.
    unsigned long time = count * fixedInterval;
    points[count++] = {pose, time};
    return true;
}

// Load trajectory points from a CSV file. Each line should contain: x,y,z,roll,pitch,yaw.
bool Trajectory::loadFromCSV(const char* filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        Serial.print("Error: Could not open file: ");
        Serial.println(filename);
        return false;
    }
    std::string line;
    // Reset current trajectory.
    count = 0;
    while (std::getline(file, line)) {
        if(line.empty()) continue;
        std::istringstream ss(line);
        std::string token;
        Pose pose;
        // Read x
        if(!std::getline(ss, token, ',')) continue;
        pose.x = std::stof(token);
        // Read y
        if(!std::getline(ss, token, ',')) continue;
        pose.y = std::stof(token);
        // Read z
        if(!std::getline(ss, token, ',')) continue;
        pose.z = std::stof(token);
        // Read roll
        if(!std::getline(ss, token, ',')) continue;
        pose.roll = std::stof(token);
        // Read pitch
        if(!std::getline(ss, token, ',')) continue;
        pose.pitch = std::stof(token);
        // Read yaw
        if(!std::getline(ss, token, ',')) continue;
        pose.yaw = std::stof(token);
        // Add the waypoint. If adding fails, break.
        if (!addWaypoint(pose)) {
            Serial.println("Error: Failed to add waypoint from CSV.");
            break;
        }
    }
    file.close();
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

void Trajectory::printPose(const Pose& pose) {
    Serial.print("Pose: "); Serial.print("x: "); Serial.print(pose.x); Serial.print(", ");
    Serial.print("y: "); Serial.print(pose.y); Serial.print(", ");
    Serial.print("z: "); Serial.print(pose.z); Serial.print(", ");
    Serial.print("roll: "); Serial.print(pose.roll); Serial.print(", ");
    Serial.print("pitch: "); Serial.print(pose.pitch); Serial.print(", ");
    Serial.print("yaw: "); Serial.print(pose.yaw); Serial.print(", ");
    Serial.print("time: "); Serial.println(millis());
}

void Trajectory::printPoints() {
    Serial.println("Trajectory Points:");
    for(int i = 0; i < count; i++) {
        Serial.print("Point "); Serial.print(i); Serial.print(": ");
        Serial.print("Time: "); Serial.print(points[i].time); Serial.print(", ");
        Serial.print("Pose: ("); Serial.print(points[i].pose.x); Serial.print(", ");
        Serial.print(points[i].pose.y); Serial.print(", ");
        Serial.print(points[i].pose.z); Serial.print(", ");
        Serial.print(points[i].pose.roll); Serial.print(", ");
        Serial.print(points[i].pose.pitch); Serial.print(", ");
        Serial.print(points[i].pose.yaw); Serial.println(")");
    }
}