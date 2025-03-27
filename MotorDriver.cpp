#include "MotorDriver.h"
#include <Arduino.h>

MotorDriver::MotorDriver(int pwm, int dir) : pwmPin(pwm), dirPin(dir) {}

void MotorDriver::begin() {
    pinMode(pwmPin, OUTPUT);
    pinMode(dirPin, OUTPUT);
}

void MotorDriver::setSpeed(float speed) {
    digitalWrite(dirPin, speed >= 0 ? HIGH : LOW);
    analogWrite(pwmPin, (int)min(abs(speed), 255.0f));
}