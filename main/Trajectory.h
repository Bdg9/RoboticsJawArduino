#ifndef TRAJECTORY_H
#define TRAJECTORY_H

#include "Kinematics.h"
#include <fstream>    // For CSV file reading
#include <sstream>
#include <string>
#include <SPI.h>
#include <SD.h>

class Trajectory {
public:
    // Constructor that sets a default interval (in milliseconds)
    Trajectory(unsigned long fixedInterval = 100);

    // Adds a waypoint with the fixed interval; time is computed automatically.
    bool addWaypoint(Pose& pose);

    // Reads waypoints from a CSV file. Each line should contain the pose parameters in a comma-separated format.
    // The time for each point is computed based on the fixed interval.
    bool loadFromCSV(const String &filename);

    // Returns the interpolated or current pose based on the current time.
    Pose getPose(unsigned long currentTime);
    void printPoints();
    void printPose(const Pose& pose);

    // Set fixed interval for trajectory points
    void setFixedInterval(unsigned long interval);
    int getFixedInterval() const;

private:
    static const int MAX_POINTS = 3500;
    struct Waypoint {
        Pose pose;
        unsigned long time;
    } points[MAX_POINTS];
    int count;
    unsigned long fixedInterval; // Fixed time interval between points (in ms)
};

#endif // TRAJECTORY_H