// Simple code to test the actuator and the encoder
// This code will move the actuator to their extended position and then to their retracted position at different speeds
// All the while printing the position of the actuator to the serial monitor

#include <Arduino.h>
#include "pin_layout.h"

#define MIN_LENGTH 0
#define MAX_LENGTH 100

#define SPEED_MAX 255
#define SPEED_MID 128
#define SPEED_SMALL 30
#define SPEED_STOP 0

#define DELAY_TIME 4000 // 4 seconds

void setup() {
    Serial.begin(9600);
    for(int i = 0; i < 6; i++) {
        pinMode(PWM_PINS[i], OUTPUT);
        pinMode(A_PINS[i], OUTPUT);
        pinMode(B_PINS[i], OUTPUT);
    }
}

void loop() {
    moveAllActuators(1, SPEED_MAX); // Move forward at max speed
    delay(DELAY_TIME); 
    stopActuators(); // Stop the actuator
    delay(1000); // Wait for 1 second

    Serial.print("Actuator extended position: ");
    printAllActuatorPositions();
    delay(10);

    moveAllActuators(-1, SPEED_MAX); // Move backward at max speed
    delay(DELAY_TIME); 
    stopActuators(); // Stop the actuator
    delay(1000); // Wait for 1 second

    Serial.print("Actuator retracted position: ");
    printAllActuatorPositions();
    delay(10);    
}

void actuatorTest(int speed, int actuatorIndex) {
    int startTime = millis();
    unsigned long lastPrintTime = 0;

    while ((millis() - startTime) < DELAY_TIME) {
        // Move to extended position
        digitalWrite(A_PINS[actuatorIndex], LOW);
        digitalWrite(B_PINS[actuatorIndex], HIGH);
        analogWrite(PWM_PINS[actuatorIndex], speed);

        // Read and print the position of the actuator every 500ms
        if (millis() - lastPrintTime >= 500) {
            lastPrintTime = millis();
            int position = analogRead(POT_PINS[actuatorIndex]);
            Serial.print("Extended position: ");
            Serial.println(position);
        }
    }

    // Stop the actuator
    digitalWrite(A_PINS[actuatorIndex], LOW);
    digitalWrite(B_PINS[actuatorIndex], LOW);
    analogWrite(PWM_PINS[actuatorIndex], SPEED_STOP);
    delay(DELAY_TIME); // Wait for 4 seconds

    startTime = millis();
    lastPrintTime = 0;

    while ((millis() - startTime) < DELAY_TIME) {
        // Move to retracted position
        digitalWrite(A_PINS[actuatorIndex], HIGH);
        digitalWrite(B_PINS[actuatorIndex], LOW);
        analogWrite(PWM_PINS[actuatorIndex], speed);

        // Read and print the position of the actuator every 500ms
        if (millis() - lastPrintTime >= 500) {
            lastPrintTime = millis();
            int position = analogRead(POT_PINS[actuatorIndex]);
            Serial.print("Retracted position: ");
            Serial.println(position);
        }
    }

    // Stop the actuator
    digitalWrite(A_PINS[actuatorIndex], LOW);
    digitalWrite(B_PINS[actuatorIndex], LOW);
    analogWrite(PWM_PINS[actuatorIndex], SPEED_STOP);
    delay(DELAY_TIME); // Wait for 4 seconds
}

void stopActuators() {
    for(int i = 0; i < 6; i++) {
        digitalWrite(A_PINS[i], LOW);
        digitalWrite(B_PINS[i], LOW);
        analogWrite(PWM_PINS[i], SPEED_STOP);
    }
}

void moveActuator(int direction, int speed, int actuatorIndex) {
    if (direction == 1) { // Move forward
        digitalWrite(A_PINS[actuatorIndex], LOW);
        digitalWrite(B_PINS[actuatorIndex], HIGH);
    } else if (direction == -1) { // Move backward
        digitalWrite(A_PINS[actuatorIndex], HIGH);
        digitalWrite(B_PINS[actuatorIndex], LOW);
    }
    analogWrite(PWM_PINS[actuatorIndex], speed);
}

void moveAllActuators(int direction, int speed) {
    for (int i = 0; i < 6; i++) {
        if (direction == 1) { // Move forward
            digitalWrite(A_PINS[i], LOW);
            digitalWrite(B_PINS[i], HIGH);
        } else if (direction == -1) { // Move backward
            digitalWrite(A_PINS[i], HIGH);
            digitalWrite(B_PINS[i], LOW);
        }
        analogWrite(PWM_PINS[i], speed);
    }
}

void printAllActuatorPositions() {
    for (int i = 0; i < 6; i++) {
        int position = analogRead(POT_PINS[i]);
        Serial.print("Actuator ");
        Serial.print(i + 1);
        Serial.print(" position: ");
        Serial.println(position);
    }
}