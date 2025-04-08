#include "Actuator.h"
#include <Arduino.h>

Actuator::Actuator(int pwmPin, int aPin, int bPin, int potPin, int actNb)
    : potPin(potPin), driver(pwmPin, aPin, bPin), minPotValue(0), maxPotValue(0), actuatorNb(actNb), targetLength(0), errorSum(0), lastError(0) {}

void Actuator::begin() {
    driver.begin();
    pinMode(potPin, INPUT);
}

float Actuator::getLength() {
    // Read the potentiometer value and store it in the buffer
    int raw = analogRead(potPin);
    pot_data_buffer[buffer_index] = raw;
    buffer_index = (buffer_index + 1) % ACT_LPF_N; // Circular buffer index

    // Calculate the average of the last ACT_LPF_N readings
    int sum = 0;
    for (int i = 0; i < ACT_LPF_N; i++) {
        sum += pot_data_buffer[i];
    }
    raw = sum / ACT_LPF_N; // Average value

    //update min/max if raw > max or raw < min
    if(raw > maxPotValue) {
        maxPotValue = raw;
        Serial.print("Warning: Actuator "); Serial.print(actuatorNb); Serial.println(" maxPotValue updated.");
    } else if(raw < minPotValue) {
        minPotValue = raw;
        Serial.print("Warning: Actuator "); Serial.print(actuatorNb); Serial.println(" minPotValue updated.");
    }
    
    // Map the raw potentiometer value to the actuator length range
    return mapFloat(raw, minPotValue, maxPotValue, (float)ACTUATOR_MIN_LENGTH, (float)ACTUATOR_MAX_LENGTH);
}

void Actuator::setTargetLength(float length) {
    targetLength = constrain(length, ACTUATOR_MIN_LENGTH, ACTUATOR_MAX_LENGTH);
}

bool Actuator::update() {
    float current = getLength();
    if(current < ACTUATOR_MIN_LENGTH || current > ACTUATOR_MAX_LENGTH) {
        driver.setSpeed(0);
        Serial.print("Error: Actuator "); Serial.print(actuatorNb); Serial.println(" out of bounds.");
        Serial.print("Current length: "); Serial.println(current);
        Serial.print("Target length: "); Serial.println(targetLength);
        Serial.print("Min length: "); Serial.println(ACTUATOR_MIN_LENGTH);
        return false;
    }
    float error = targetLength - current;
    errorSum += error * (PLATFORM_UPDATE_INTERVAL / 1000.0f);
    float dError = (error - lastError) / (PLATFORM_UPDATE_INTERVAL / 1000.0f);
    float output = ACT_KP * error + ACT_KI * errorSum + ACT_KD * dError;
    driver.setSpeed(output);
    lastError = error;
    Serial.print("Actuator "); Serial.print(actuatorNb); 
    Serial.print(" target speed: "); Serial.print(output);
    Serial.print(", target length: "); Serial.print(targetLength);
    Serial.print(", current length: "); Serial.println(current);
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