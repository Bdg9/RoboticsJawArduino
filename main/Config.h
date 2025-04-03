#ifndef CONFIG_H
#define CONFIG_H

#define NUM_ACTUATORS 6
#define CALIB_TIME 10000 //ms
#define CALIB_MIN_DIF 100

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
const int ACT_PWM_PINS[NUM_ACTUATORS] = {35, 8, 5, 2, 29, 26};
const int ACT_A_PINS[NUM_ACTUATORS] = {34, 7, 4, 1, 28, 25};
const int ACT_B_PINS[NUM_ACTUATORS] = {33, 6, 3, 0, 27, 24};
const int ACT_POT_PINS[NUM_ACTUATORS] = {22, 21, 20, 18, 17, 16};

// Constraints for the pose
const float MIN_X = -20.0f;
const float MAX_X = 20.0f;

const float MIN_Y = -20.0f;
const float MAX_Y = 20.0f;

const float MIN_Z = 0.0f;
const float MAX_Z = 60.0f;

const float MIN_ROLL = -5.0f;
const float MAX_ROLL = 35.0f;

const float MIN_PITCH = -20.0f;
const float MAX_PITCH = 20.0f;

const float MIN_YAW = -10.0f;
const float MAX_YAW = 10.0f;

#endif // CONFIG_H