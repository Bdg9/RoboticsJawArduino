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

void StewartPlatform::calibrate(bool debug) {
    Serial.println("Calibrating actuators...");

    //extend all actuators
    int time = millis();
    while (millis() - time < CALIB_TIME) {
        for(int i = 0; i < NUM_ACTUATORS; i++) {
            actuators[i]->setSpeed(255);
        }
        if(debug) {
            Serial.print("Actuator 4 pot : "); Serial.println(analogRead(actuators[4]->potPin)); //debug
        }
    }

    for(int i = 0; i < NUM_ACTUATORS; i++) {
        actuators[i]->stop();
    }

    delay(10);

    for (int i = 0; i < NUM_ACTUATORS; i++) {
        int min = analogRead(actuators[i]->potPin);
        for(int j = 0; j < 10; j++) {
            int raw = analogRead(actuators[i]->potPin);
            if(raw < min) {
                min = raw;
            }
        }
        actuators[i]->setMin(min);
        if(debug) {
            Serial.print("Actuator "); Serial.print(i); Serial.print(": minPotValue = "); Serial.println(min);
        }
    }

    Serial.println("retracting all");

    //retract all actuators
    time = millis();
    while (millis() - time < CALIB_TIME) {
        for(int i = 0; i < NUM_ACTUATORS; i++) {
            actuators[i]->setSpeed(-255);
        }
        if(debug) {
            Serial.print("Actuator 4 pot : "); Serial.println(analogRead(actuators[4]->potPin)); //debug
        }
    }

    for(int i = 0; i < NUM_ACTUATORS; i++) {
        actuators[i]->stop();
    }

    for (int i = 0; i < NUM_ACTUATORS; i++) {
        int max = analogRead(actuators[i]->potPin);
        for(int j = 0; j < 10; j++) {
            int raw = analogRead(actuators[i]->potPin);
            if(raw > max) {
                max = raw;
            }
        }
        actuators[i]->setMax(max);
        if(debug) {
            Serial.print("Actuator "); Serial.print(i); Serial.print(": maxPotValue = "); Serial.println(max);
        }
    }
    
}