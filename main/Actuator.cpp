#include "Actuator.h"
#include <Arduino.h>

Actuator::Actuator(CD74HC4067& pot_mux, int pwmPin, int aPin, int bPin, int potPin, int actNb)
    : pot_mux(pot_mux), potPin(potPin), driver(pwmPin, aPin, bPin), minPotValue(0), maxPotValue(0), actuatorNb(actNb), targetLength(0), errorSum(0), lastError(0) {}

void Actuator::begin() {
    driver.begin();
    loadCalibration();
    std::fill(length_data_buffer, length_data_buffer + ACT_LPF_N, (float)ACTUATOR_MIN_LENGTH); // Initialize the buffer to zero
}

void Actuator::loadCalibration() {
    // Build filename e.g., "/robotics_jaw/cal_act1.txt" for actuator 1.
    String filename = String(SD_ROOT) + "cal_act" + String(actuatorNb) + ".txt";
    if (SD.exists(filename.c_str())) {
        File calFile = SD.open(filename.c_str(), FILE_READ);
        if (calFile) {
            // Read the first two lines: the first line for min and the second for max.
            // TODO: now that we calibrate min at each boot, we can remove the first line.
            String minLine = calFile.readStringUntil('\n');
            String maxLine = calFile.readStringUntil('\n');
            minPotValue = minLine.toInt();
            maxPotValue = maxLine.toInt();
            Serial.print("Actuator ");
            Serial.print(actuatorNb);
            Serial.println(" calibration loaded:");
            Serial.print("Min: ");
            Serial.println(minPotValue);
            Serial.print("Max: ");
            Serial.println(maxPotValue);
            calFile.close();
        } else {
            Serial.print("Actuator ");
            Serial.print(actuatorNb);
            Serial.println(" calibration file exists but failed to open.");
        }
    } else {
        Serial.print("Error: Actuator ");
        Serial.print(actuatorNb);
        Serial.println(" calibration file not found.");
        // TODO: Handle the case where the calibration file does not exist.
    }
}

void Actuator::saveCalibration() {
    // Build filename e.g., "/robotics_jaw/cal_act1.txt" for actuator 1.
    String filename = String(SD_ROOT) + "cal_act" + String(actuatorNb) + ".txt";
    // Remove the file first if it exists to ensure a fresh write.
    if(SD.exists(filename.c_str())) {
        SD.remove(filename.c_str());
    }
    File calFile = SD.open(filename.c_str(), FILE_WRITE);
    if (calFile) {
        calFile.println(minPotValue);
        calFile.println(maxPotValue);
        calFile.close();
        Serial.print("Calibration saved for Actuator ");
        Serial.println(actuatorNb);
    } else {
        Serial.print("Error: Could not open calibration file for Actuator ");
        Serial.println(actuatorNb);
    }
}

float Actuator::getLength(bool verbose) {
    // Read the potentiometer value and store it in the buffer
    pot_mux.channel(potPin); // Select the correct channel for this actuator
    int raw = analogRead(POT_MUX_SIG);

    float length = mapFloat(raw, minPotValue, maxPotValue, (float)ACTUATOR_MIN_LENGTH, (float)ACTUATOR_MAX_LENGTH);

    // Apply low pass filter to smooth the reading
    length_data_buffer[buffer_index] = length;
    buffer_index = (buffer_index + 1) % ACT_LPF_N; // Circular buffer index

    // Calculate the average of the last ACT_LPF_N readings if the buffer is full
    float sum = 0;
    for(int i = 0; i < ACT_LPF_N; i++) {
        sum += length_data_buffer[i];
    }
    float filtered_length = sum / ACT_LPF_N;

    if(verbose) {
        Serial.print("Debug Actuator "); Serial.print(actuatorNb);
        Serial.print(" raw pot value: "); Serial.print(raw);
        Serial.print(", length: "); Serial.print(length);
        Serial.print(", filtered length: "); Serial.print(filtered_length);
        Serial.print(" time: "); Serial.println(millis());
    }
    
    return filtered_length;
}

int Actuator::getRaw() {
    pot_mux.channel(potPin); // Select the correct channel for this actuator
    return analogRead(POT_MUX_SIG);
}

void Actuator::setTargetLength(float length) {
    targetLength = constrain(length, ACTUATOR_MIN_LENGTH, ACTUATOR_MAX_LENGTH);
}

bool Actuator::update(bool verbose) {
    float current = getLength(false);
    // if(current < ACTUATOR_MIN_LENGTH || current > ACTUATOR_MAX_LENGTH) {
    //     driver.setSpeed(0);
    //     Serial.print("Error: Actuator "); Serial.print(actuatorNb); Serial.println(" out of bounds.");
    //     Serial.print("Current length: "); Serial.println(current);
    //     Serial.print("Target length: "); Serial.println(targetLength);
    //     Serial.print("Min length: "); Serial.println(ACTUATOR_MIN_LENGTH);
    //     return false;
    // }
    float error = targetLength - current;
    errorSum += error * (PLATFORM_UPDATE_INTERVAL / 1000.0f);
    errorSum = constrain(errorSum, -MAX_INTEGRAL, MAX_INTEGRAL); // Prevent integral windup
    float dError = (error - lastError) / (PLATFORM_UPDATE_INTERVAL / 1000.0f);
    float output = ACT_KP * error + ACT_KI * errorSum + ACT_KD * dError;
    driver.setSpeed(output);
    lastError = error;
    if (verbose) {
        Serial.print("Actuator "); Serial.print(actuatorNb); 
        Serial.print(" target speed: "); Serial.print((int)min(abs(output), 255.0f));
        Serial.print(", target length: "); Serial.print(targetLength);
        Serial.print(", current length: "); Serial.print(current);
        Serial.print(", time: "); Serial.println(millis());
    }
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