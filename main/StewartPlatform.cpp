#include "StewartPlatform.h"
#include "Config.h"
#include <Arduino.h>

StewartPlatform::StewartPlatform(): pot_mux(POT_MUX_S0, POT_MUX_S1, POT_MUX_S2, POT_MUX_S3) {
    pinMode(POT_MUX_SIG, INPUT); // Mux SIG pin for potentiometers
    pinMode(POT_MUX_EN, OUTPUT); // Mux EN pin for potentiometers
    digitalWrite(POT_MUX_EN, LOW); // Enable the potentiometer Mux
    for(int i = 0; i < 6; i++)
        actuators[i] = new Actuator(pot_mux, ACT_PWM_PINS[i], ACT_A_PINS[i], ACT_B_PINS[i], ACT_POT_CH[i], i);
}

void StewartPlatform::begin() {
    for(int i = 0; i < 6; i++) actuators[i]->begin();
    kin.setRotationCenter(ROTATION_CENTER_X, ROTATION_CENTER_Y, ROTATION_CENTER_Z);
    kin.setHomePose({0, 0, Z0+5, 0, 0, 0}); // Set home pose with Z0
}

void StewartPlatform::moveToPose(const Pose& pose, bool absolute) {
    kin.inverse(pose, targetLengths, absolute);
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

bool StewartPlatform::update(bool verbose) {
    for(int i = 0; i < 6; i++){
        if(!actuators[i]->update(verbose)) return false;       
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

bool StewartPlatform::calibrateActuators(bool fullCalibration, bool debug) {
    if (fullCalibration) {
        Serial.println("Calibrating actuators (full stroke)...");

        // Extend all actuators to set max values.
        int startTime = millis();
        while (millis() - startTime < CALIB_TIME) {
            for (int i = 0; i < NUM_ACTUATORS; i++) {
                actuators[i]->setSpeed(255);
            }
        }
        for (int i = 0; i < NUM_ACTUATORS; i++) {
            actuators[i]->stop();
        }
        delay(10);

        // Compute max values from extended position.
        for (int i = 0; i < NUM_ACTUATORS; i++) {
            pot_mux.channel(actuators[i]->potPin);
            int max_val = analogRead(POT_MUX_SIG);
            for (int j = 0; j < 10; j++) {
                pot_mux.channel(actuators[i]->potPin);
                int raw = analogRead(POT_MUX_SIG);
                if (raw > max_val) {
                    max_val = raw;
                }
            }
            actuators[i]->setMax(max_val);
            if (debug) {
                Serial.print("Actuator ");
                Serial.print(i);
                Serial.print(": maxPotValue = ");
                Serial.println(max_val);
            }
        }
    }

    // Retract actuators to set min values.
    if (fullCalibration)
        Serial.println("Retracting actuators for min calibration...");
    else
        Serial.println("Calibrating actuators (min only)...");

    int startTime = millis();
    while (millis() - startTime < CALIB_TIME) {
        for (int i = 0; i < NUM_ACTUATORS; i++) {
            actuators[i]->setSpeed(-255);
        }
    }
    for (int i = 0; i < NUM_ACTUATORS; i++) {
        actuators[i]->stop();
    }

    // Compute min values from retracted position.
    for (int i = 0; i < NUM_ACTUATORS; i++) {
            pot_mux.channel(actuators[i]->potPin);
            int min_val = analogRead(POT_MUX_SIG);
        for (int j = 0; j < 10; j++) {
            pot_mux.channel(actuators[i]->potPin);
            int raw = analogRead(POT_MUX_SIG);
            if (raw < min_val) {
                min_val = raw;
            }
        }
        actuators[i]->setMin(min_val);
        if (debug) {
            Serial.print("Actuator ");
            Serial.print(i);
            Serial.print(": minPotValue = ");
            Serial.println(min_val);
        }

        if (min_val > actuators[i]->getMax()) {
            Serial.print("Error: Actuator ");
            Serial.print(i);
            Serial.print(" min potentiometer value (");
            Serial.print(min_val);
            Serial.print(") > max potentiometer value (");
            Serial.print(actuators[i]->getMax());
            Serial.println(")");
            return false;
        } else if ((actuators[i]->getMax() - min_val) < CALIB_MIN_DIF) {
            Serial.print("Error: Actuator ");
            Serial.print(i);
            Serial.println(", not enough difference between min and max pot values.");
            return false;
        } else if (min_val > CALIB_PIN_NOT_WORKING) {
            Serial.print("Error: Actuator ");
            Serial.print(i);
            Serial.print(" min potentiometer value (");
            Serial.print(min_val);
            Serial.print(") is too high, pin may be not working.");
            return false;
        }
    }

    // Save calibration data to SD card only if full calibration is requested.
    if (fullCalibration) {
        for (int i = 0; i < NUM_ACTUATORS; i++) {
            actuators[i]->saveCalibration();
        }
    }

    Serial.println("Calibration done.");
    return true;
}