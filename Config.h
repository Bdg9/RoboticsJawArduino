#ifndef CONFIG_H
#define CONFIG_H

// Geometry (units in mm)
const float BASE_JOINTS[6][3] = {
    {100, 0, 0}, {50, 86.6, 0}, {-50, 86.6, 0}, {-100, 0, 0}, {-50, -86.6, 0}, {50, -86.6, 0}
};

const float PLATFORM_JOINTS[6][3] = {
    {30, 0, 0}, {15, 25.98, 0}, {-15, 25.98, 0}, {-30, 0, 0}, {-15, -25.98, 0}, {15, -25.98, 0}
};

const float ACTUATOR_MIN_LENGTH = 50.0f;
const float ACTUATOR_MAX_LENGTH = 200.0f;

// PID constants
const float ACT_KP = 2.0f;
const float ACT_KI = 0.0f;
const float ACT_KD = 0.1f;

// Update interval (ms)
const unsigned long PLATFORM_UPDATE_INTERVAL = 10;

// Pin assignments (customize before upload)
const int ACT_PWM_PINS[6] = {2, 3, 4, 5, 6, 7};
const int ACT_DIR_PINS[6] = {8, 9, 10, 11, 12, 13};
const int ACT_POT_PINS[6] = {A0, A1, A2, A3, A4, A5};

#endif // CONFIG_H