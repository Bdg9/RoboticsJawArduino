#ifndef ACTUATOR_H
#define ACTUATOR_H

#include "MotorDriver.h"
#include "Utils.h"
#include "Config.h"

class Actuator {
public:
    Actuator(int pwmPin, int aPin, int bPin, int potPin, int actNb);
    void begin();
    void setTargetLength(float length);
    bool update();
    float getLength();
    void stop();
    void setSpeed(int speed);
    void setMin(int min);
    void setMax(int max);
    inline int getMin(){ return minPotValue; }
    inline int getMax(){ return maxPotValue; }
    int potPin;
private:
    MotorDriver driver;
    int minPotValue;
    int maxPotValue;
    int actuatorNb;
    float targetLength;
    float errorSum;
    float lastError;
    int pot_data_buffer[ACT_LPF_N]; // Buffer for the last 10 readings
    int buffer_index = 0; // Index for the next reading to be added to the buffer
};

#endif // ACTUATOR_H