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
const int ACT_POT_CH[NUM_ACTUATORS] = {0, 1, 2, 3, 4, 5};
const int PWM_FREQ = 23000; // 23kHz

// multiplexer configuration
const int LC_MUX_S0 = 26; // Mux S0 pin
const int LC_MUX_S1 = 25; // Mux S1 pin
const int LC_MUX_S2 = 14; // Mux S2 pin
const int LC_MUX_S3 = 13; // Mux S3 pin
const int LC_MUX_SIG = 41; // Mux SIG pin
const int LC_MUX_EN = 17; // Mux EN pin 
// Multiplexer channel for the load cell
const int LC_FRONT[3] = {9, 8, 7}; // A, Mux channel for front load cell (x, y, z)
const int LC_BACK_R[3] = {12, 11, 10}; // B, Mux channel for back right load cell (x, y, z)
const int LC_BACK_L[3] = {15, 14, 13}; // C, Mux channel for back left load cell (x, y, z)
// Load cell samples
const int LC_SAMPLES = 10; // Number of samples to average for load cell readings
// Load cell calibration
const int LOAD_CELL_MIN_FORCE = 0; // Minimum load cell value
const int LOAD_CELL_MAX_FORCE = 500; // Maximum load cell value
const int LOAD_CELL_MIN = 0; // Minimum load cell ADC value
const int LOAD_CELL_MAX = 1023; // Maximum load cell ADC value

// Actuator potentiometer mux configuration
const int POT_MUX_S0 = 22; // Mux S0 pin for potentiometers
const int POT_MUX_S1 = 21; // Mux S1 pin for potentiometers
const int POT_MUX_S2 = 20; // Mux S2 pin for potentiometers
const int POT_MUX_S3 = 19; // Mux S3 pin for potentiometers
const int POT_MUX_SIG = 18; // Mux SIG pin for potentiometers
const int POT_MUX_EN = 23; // Mux EN pin for potentiometers


// Constraints for the pose
const float MIN_X = -20.0f;
const float MAX_X = 20.0f;

const float MIN_Y = -20.0f;
const float MAX_Y = 20.0f;

const float MIN_Z = -30.0f;
const float MAX_Z = 5.0f;

const float MIN_ROLL = degrees2rad(-35.0f);
const float MAX_ROLL = degrees2rad(10.0f);

const float MIN_PITCH = degrees2rad(-20.0f);
const float MAX_PITCH = degrees2rad(20.0f);

const float MIN_YAW = degrees2rad(-20.0f);
const float MAX_YAW = degrees2rad(10.0f);

const int MIN_SPEED = 20;

// Center of rotation
const float ROTATION_CENTER_X = 0.0f;
const float ROTATION_CENTER_Y = 102.0f;
const float ROTATION_CENTER_Z = 83.0f;

#endif // CONFIG_H