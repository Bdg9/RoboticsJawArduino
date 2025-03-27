#include "Actuator.h"
#include "Config.h"
#include <Arduino.h>

Actuator::Actuator(int pwmPin, int aPin, int bPin, int potPin, int actNb)
    : driver(pwmPin, aPin, bPin), potPin(potPin), actuatorNb(actNb), targetLength(0), errorSum(0), lastError(0), minPotValue(0), maxPotValue(0) {}

void Actuator::begin() {
    driver.begin();
    pinMode(potPin, INPUT);
}

float Actuator::getLength() const {
    int raw = analogRead(potPin);
    return map(raw, minPotValue, maxPotValue, (int)ACTUATOR_MIN_LENGTH, (int)ACTUATOR_MAX_LENGTH);
}

void Actuator::setTargetLength(float length) {
    targetLength = constrain(length, ACTUATOR_MIN_LENGTH, ACTUATOR_MAX_LENGTH);
}

void Actuator::update() {
    float current = getLength();
    if(current < ACTUATOR_MIN_LENGTH || current > ACTUATOR_MAX_LENGTH) {
        driver.setSpeed(0);
        return;
    }
    float error = targetLength - current;
    errorSum += error * (PLATFORM_UPDATE_INTERVAL / 1000.0f);
    float dError = (error - lastError) / (PLATFORM_UPDATE_INTERVAL / 1000.0f);
    float output = ACT_KP * error + ACT_KI * errorSum + ACT_KD * dError;
    driver.setSpeed(output);
    lastError = error;
}

void Actuator::stop() {
    driver.setSpeed(0);
}

void Actuator::calibrate(bool debug) {
    if(debug) Serial.println("Calibrating actuator " + String(actuatorNb) + "...");
    //extend actuator until it hits the limit switch
    driver.setSpeed(255);
    delay(CALIB_TIME);

    //sample 10 pot values and set max
    maxPotValue = analogRead(potPin);
    for(int i = 0; i < 10; i++) {
        int val = analogRead(potPin);
        if(val > maxPotValue) maxPotValue = val;
        delay(100);
    }

    //retract actuator until it hits the limit switch
    driver.setSpeed(-255);
    delay(CALIB_TIME);

    //sample 10 pot values and set min
    minPotValue = analogRead(potPin);
    for(int i = 0; i < 10; i++) {
        int val = analogRead(potPin);
        if(val < minPotValue) minPotValue = val;
        delay(100);
    }

    //stop actuator
    driver.setSpeed(0);

    if(debug) {
        Serial.print("Calibration complete for actuator " + String(actuatorNb) + ". Min pot value: ");
        Serial.print(minPotValue);
        Serial.print(", max pot value: ");
        Serial.println(maxPotValue);
    }
}