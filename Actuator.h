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
    void calibrate(bool debug=false);
private:
    MotorDriver driver;
    int potPin;
    int minPotValue;
    int maxPotValue;
    int actuatorNb;
    float targetLength;
    float errorSum;
    float lastError;
};

#endif // ACTUATOR_H