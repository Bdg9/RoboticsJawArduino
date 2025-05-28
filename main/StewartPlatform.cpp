#include "StewartPlatform.h"
#include "Config.h"
#include <Arduino.h>

StewartPlatform::StewartPlatform() {
    for(int i = 0; i < 6; i++)
        actuators[i] = new Actuator(ACT_PWM_PINS[i], ACT_A_PINS[i], ACT_B_PINS[i], ACT_POT_PINS[i], i);
}

void StewartPlatform::begin() {
    for(int i = 0; i < 6; i++) actuators[i]->begin();
    kin.setRotationCenter(0, 102.0f, 83.0f);
    kin.setHomePose({0, -50, 0, 0, 0, 0}); // Set home pose with Z0
}

void StewartPlatform::moveToPose(const Pose& pose) {
    kin.inverse(pose, targetLengths);
    for(int i = 0; i < 6; i++) {
        float clamped = constrain(targetLengths[i], ACTUATOR_MIN_LENGTH, ACTUATOR_MAX_LENGTH);
        if(clamped != targetLengths[i]) {
            Serial.print("Warning: actuator "); Serial.print(i);
            Serial.print(" target length out of range, clamped.");
            Serial.print(" Target: "); Serial.print(targetLengths[i]);
            Serial.print(" Clamped: "); Serial.println(clamped);
        }
        actuators[i]->setTargetLength(clamped);
    }
}

bool StewartPlatform::update() {
    for(int i = 0; i < 6; i++){
        if(!actuators[i]->update()) return false;       
    }
    return true;
}

void StewartPlatform::stop() {
    for(int i = 0; i < 6; i++) actuators[i]->stop();
}

// State StewartPlatform::getState() const {
//     return state;
// }

// bool StewartPlatform::setState(State newState) {
//     if (newState == CALIBRATING) {
//         for (int i = 0; i < NUM_ACTUATORS; i++) {
//             actuators[i]->stop();
//         }
//     }
//     state = newState;
//     return true;
// }

bool StewartPlatform::calibrateActuators(bool debug) {
    Serial.println("Calibrating actuators...");

    // Extend all actuators
    int time = millis();
    while (millis() - time < CALIB_TIME) {
        for (int i = 0; i < NUM_ACTUATORS; i++) {
            actuators[i]->setSpeed(255);
        }
    }

    for (int i = 0; i < NUM_ACTUATORS; i++) {
        actuators[i]->stop();
    }

    delay(10);

    // Set max values (extended position)
    for (int i = 0; i < NUM_ACTUATORS; i++) {
        int max = analogRead(actuators[i]->potPin);
        for (int j = 0; j < 10; j++) {
            int raw = analogRead(actuators[i]->potPin);
            if (raw > max) {
                max = raw;
            }
        }
        actuators[i]->setMax(max);
        if (debug) {
            Serial.print("Actuator ");
            Serial.print(i);
            Serial.print(": maxPotValue = ");
            Serial.println(max);
        }
    }

    // Retract all actuators
    time = millis();
    while (millis() - time < CALIB_TIME) {
        for (int i = 0; i < NUM_ACTUATORS; i++) {
            actuators[i]->setSpeed(-255);
        }
    }

    for (int i = 0; i < NUM_ACTUATORS; i++) {
        actuators[i]->stop();
    }

    // Set min values (retracted position)
    for (int i = 0; i < NUM_ACTUATORS; i++) {
        int min = analogRead(actuators[i]->potPin);
        for (int j = 0; j < 10; j++) {
            int raw = analogRead(actuators[i]->potPin);
            if (raw < min) {
                min = raw;
            }
        }
        actuators[i]->setMin(min);
        if (debug) {
            Serial.print("Actuator ");
            Serial.print(i);
            Serial.print(": minPotValue = ");
            Serial.println(min);
        }
        if (min > actuators[i]->getMax()) {
            Serial.print("Error: Actuator ");
            Serial.print(i);
            Serial.print(" min potentiometer value (");
            Serial.print(min);
            Serial.print(") > max potentiometer value (");
            Serial.print(actuators[i]->getMax());
            Serial.println(")");
            return false;
        } else if ((actuators[i]->getMax() - min) < CALIB_MIN_DIF) {
            Serial.print("Error: Actuator ");
            Serial.print(i);
            Serial.println(", not enough difference between min and max pot values.");
            return false;
        }
    }

    // Serial.println("Saving calibration in SD card.");
    // for (int i = 0; i < NUM_ACTUATORS; i++) {
    //     actuators[i]->saveCalibration();
    // }
    Serial.println("Calibration done.");
    return true;
}