#include "StewartPlatform.h"
#include "Config.h"
#include <Arduino.h>

StewartPlatform::StewartPlatform() {
    for(int i = 0; i < 6; i++)
        actuators[i] = new Actuator(ACT_PWM_PINS[i], ACT_A_PINS[i], ACT_B_PINS[i], ACT_POT_PINS[i], i);
}

void StewartPlatform::begin() {
    for(int i = 0; i < 6; i++) actuators[i]->begin();
}

void StewartPlatform::moveToPose(const Pose& pose) {
    Kinematics::inverse(pose, targetLengths);
    for(int i = 0; i < 6; i++) {
        float clamped = constrain(targetLengths[i], ACTUATOR_MIN_LENGTH, ACTUATOR_MAX_LENGTH);
        if(clamped != targetLengths[i]) {
            Serial.print("Warning: actuator "); Serial.print(i);
            Serial.println(" target length out of range, clamped.");
        }
        actuators[i]->setTargetLength(clamped);
    }
}

void StewartPlatform::update() {
    for(int i = 0; i < 6; i++) actuators[i]->update();
}

void StewartPlatform::calibrateActuators(bool debug) {
    for(int i = 0; i < 6; i++) actuators[i]->calibrate(debug);
}