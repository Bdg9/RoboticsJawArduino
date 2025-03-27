#include "MotorDriver.h"
#include <Arduino.h>

MotorDriver::MotorDriver(int pwm, int in1, int in2) : pwmPin(pwm), in1Pin(in1), in2Pin(in2) {}

void MotorDriver::begin() {
    pinMode(pwmPin, OUTPUT);
    pinMode(in1Pin, OUTPUT);
    pinMode(in2Pin, OUTPUT);
}

void MotorDriver::setSpeed(float speed) {
    digitalWrite(dirPin, speed >= 0 ? HIGH : LOW);
    analogWrite(pwmPin, (int)min(abs(speed), 255.0f));
}