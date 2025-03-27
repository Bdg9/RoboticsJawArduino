#include "Actuator.h"
#include "Config.h"
#include <Arduino.h>

Actuator::Actuator(int pwmPin, int dirPin, int potPin)
    : driver(pwmPin, dirPin), potPin(potPin), targetLength(0), errorSum(0), lastError(0) {}

void Actuator::begin() {
    driver.begin();
    pinMode(potPin, INPUT);
}

float Actuator::getLength() const {
    int raw = analogRead(potPin);
    return map(raw, 0, 1023, (int)ACTUATOR_MIN_LENGTH, (int)ACTUATOR_MAX_LENGTH);
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