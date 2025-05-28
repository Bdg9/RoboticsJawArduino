#ifndef CONFIG_H
#define CONFIG_H

#include "Utils.h"

// SD card configuration
#define SD_CS BUILTIN_SDCARD  // Builtin SD card number for Teensy 4.1
const char SD_ROOT[] = "/robotics_jaw/"; // Path to the SD card directory

#define NUM_ACTUATORS 6
#define CALIB_TIME 10000 //ms
#define CALIB_MIN_DIF 100
#define CALIB_PIN_NOT_WORKING 600

// Geometry (units in mm)
const float BASE_JOINTS[NUM_ACTUATORS][3] = {
    {215, 147.224, 0}, {235, 112.583, 0}, {20, -259.808, 0}, {-20, -259.808, 0}, {-235, 112.583, 0}, {-215, 147.224, 0}
};

const float PLATFORM_JOINTS[NUM_ACTUATORS][3] = {
    {20, 147.224, 0}, {137.5, -56.292, 0}, {117.5, -90.933, 0}, {-117.5, -90.933, 0}, {-137.5, -56.292, 0}, {-20, 147.224, 0}
};

const float ACTUATOR_MIN_LENGTH = 378.640f;
const float ACTUATOR_MAX_LENGTH = 480.240f;
const float Z0 = 324.415f;

// PID constants
const float ACT_KP = 25.0f;
const float ACT_KI = 0.1f;
const float ACT_KD = 0.0f;
const float MAX_INTEGRAL = 100.0f; // Maximum integral term to prevent windup

// Low pass filter constant
const int ACT_LPF_N = 10; // Number of samples to average

// Update interval (ms)
const unsigned long PLATFORM_UPDATE_INTERVAL = 10;

// Pin assignments 
const int ACT_PWM_PINS[NUM_ACTUATORS] = {33, 8, 5, 2, 29, 25};
const int ACT_A_PINS[NUM_ACTUATORS] = {34, 12, 4, 1, 28, 26};
const int ACT_B_PINS[NUM_ACTUATORS] = {36, 6, 3, 0, 27, 24};
const int ACT_POT_PINS[NUM_ACTUATORS] = {23, 21, 40, 17, 16, 41};
const int PWM_FREQ = 23000; // 23kHz

// Constraints for the pose
const float MIN_X = -20.0f;
const float MAX_X = 20.0f;

const float MIN_Y = -20.0f;
const float MAX_Y = 20.0f;

const float MIN_Z = Z0 + 0.0f;
const float MAX_Z = Z0 + 60.0f;

const float MIN_ROLL = degrees2rad(-35.0f);
const float MAX_ROLL = degrees2rad(5.0f);

const float MIN_PITCH = degrees2rad(-20.0f);
const float MAX_PITCH = degrees2rad(20.0f);

const float MIN_YAW = degrees2rad(-10.0f);
const float MAX_YAW = degrees2rad(10.0f);

const int MIN_SPEED = 20;

// Center of rotation
const float ROTATION_CENTER_X = 0.0f;
const float ROTATION_CENTER_Y = 102.0f;
const float ROTATION_CENTER_Z = 83.0f;

#endif // CONFIG_H