#include "MotorDriver.h"
#include <Arduino.h>

MotorDriver::MotorDriver(int pwm, int a, int b) : pwmPin(pwm), aPin(a), bPin(b) {}

void MotorDriver::begin() {
    pinMode(pwmPin, OUTPUT);
    pinMode(aPin, OUTPUT);
    pinMode(bPin, OUTPUT);
}

void MotorDriver::setSpeed(float speed) {
    digitalWrite(aPin, speed >= 0 ? HIGH : LOW); //to test
    digitalWrite(bPin, speed >= 0 ? LOW : HIGH);
    analogWrite(pwmPin, (int)min(abs(speed), 255.0f));
}

void MotorDriver::stop() {
    digitalWrite(aPin, LOW);
    digitalWrite(bPin, LOW);
    analogWrite(pwmPin, 0);
}