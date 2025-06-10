#include "MotorDriver.h"
#include <Arduino.h>
#include "Config.h"

MotorDriver::MotorDriver(int pwm, int a, int b) : pwmPin(pwm), aPin(a), bPin(b) {}

void MotorDriver::begin() {
    pinMode(pwmPin, OUTPUT);
    analogWriteFrequency(pwmPin, PWM_FREQ); 
    pinMode(aPin, OUTPUT);
    pinMode(bPin, OUTPUT);
}

void MotorDriver::setSpeed(float speed) {
    digitalWrite(aPin, speed >= 0 ? LOW : HIGH); 
    digitalWrite(bPin, speed >= 0 ? HIGH : LOW);
    if(abs(speed) < MIN_SPEED){ speed = 0; } 
    analogWrite(pwmPin, (int)min(abs(speed), 255.0f));
}

void MotorDriver::stop() {
    digitalWrite(aPin, LOW);
    digitalWrite(bPin, LOW);
    analogWrite(pwmPin, 0);
}