#ifndef ACTUATOR_H
#define ACTUATOR_H

#include "MotorDriver.h"

class Actuator {
public:
    Actuator(int pwmPin, int aPin, int bPin, int potPin, int actNb);
    void begin();
    void setTargetLength(float length);
    void update();
    float getLength() const;
    void stop();
    void setSpeed(int speed);
    void setMin(int min);
    void setMax(int max);
    int potPin;
private:
    MotorDriver driver;
    int minPotValue;
    int maxPotValue;
    int actuatorNb;
    float targetLength;
    float errorSum;
    float lastError;
};

#endif // ACTUATOR_H