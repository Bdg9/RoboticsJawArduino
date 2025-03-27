#ifndef CONFIG_H
#define CONFIG_H

#define NUM_ACTUATORS 6

// Geometry (units in mm)
const float BASE_JOINTS[NUM_ACTUATORS][3] = {
    {215, 147.224, 0}, {235, 112.583, 0}, {20, -259.808, 0}, {-20, -259.808, 0}, {-235, 112.583, 0}, {-215, -147.224, 0}
};

const float PLATFORM_JOINTS[NUM_ACTUATORS][3] = {
    {20, 147.224, 0}, {137.5, -56.292, 0}, {117.5, -90.933, 0}, {-117.5, -90.933, 0}, {-137.5, -56.292, 0}, {-20, 147.224, 0}
};

const float ACTUATOR_MIN_LENGTH = 277.955f;
const float ACTUATOR_MAX_LENGTH = 379.555f;

// PID constants
const float ACT_KP = 2.0f;
const float ACT_KI = 0.0f;
const float ACT_KD = 0.1f;

// Update interval (ms)
const unsigned long PLATFORM_UPDATE_INTERVAL = 10;

// Pin assignments 
const int ACT_PWM_PINS[NUM_ACTUATORS] = {28, 12, 29, 6, 5, 0};
const int ACT_A_PINS[NUM_ACTUATORS] = {27, 25, 30, 8, 4, 2};
const int ACT_B_PINS[NUM_ACTUATORS] = {26, 24, 31, 7, 3, 1};
const int ACT_POT_PINS[NUM_ACTUATORS] = {23, 22, 21, 20, 19, 18};

#endif // CONFIG_H