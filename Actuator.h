#ifndef ACTUATOR_H
#define ACTUATOR_H

#include "MotorDriver.h"

class Actuator {
public:
    Actuator(int pwmPin, int dirPin, int potPin);
    void begin();
    void setTargetLength(float length);
    void update();
    float getLength() const;
private:
    MotorDriver driver;
    int potPin;
    float targetLength;
    float errorSum;
    float lastError;
};

#endif // ACTUATOR_H