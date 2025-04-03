#include "Actuator.h"
#include "Config.h"
#include <Arduino.h>

Actuator::Actuator(int pwmPin, int aPin, int bPin, int potPin, int actNb)
    : potPin(potPin), driver(pwmPin, aPin, bPin), minPotValue(0), maxPotValue(0), actuatorNb(actNb), targetLength(0), errorSum(0), lastError(0) {}

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

bool Actuator::update() {
    float current = getLength();
    if(current < ACTUATOR_MIN_LENGTH || current > ACTUATOR_MAX_LENGTH) {
        driver.setSpeed(0);
        Serial.print("Error: Actuator "); Serial.print(actuatorNb); Serial.println(" out of bounds.");
        return false;
    }
    float error = targetLength - current;
    errorSum += error * (PLATFORM_UPDATE_INTERVAL / 1000.0f);
    float dError = (error - lastError) / (PLATFORM_UPDATE_INTERVAL / 1000.0f);
    float output = ACT_KP * error + ACT_KI * errorSum + ACT_KD * dError;
    driver.setSpeed(output);
    lastError = error;
    return true;
}

void Actuator::stop() {
    driver.setSpeed(0);
}

void Actuator::setSpeed(int speed) {
    driver.setSpeed(speed);
}

void Actuator::setMin(int min) {
    minPotValue = min;
}

void Actuator::setMax(int max) {
    maxPotValue = max;
}