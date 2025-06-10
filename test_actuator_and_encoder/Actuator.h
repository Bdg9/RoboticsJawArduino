#ifndef ACTUATOR_H
#define ACTUATOR_H

#include "MotorDriver.h"
#include "Utils.h"
#include "Config.h"
#include <SPI.h>
#include <SD.h>
#include <CD74HC4067.h>


class Actuator {
public:
    Actuator(CD74HC4067& pot_mux, int pwmPin, int aPin, int bPin, int potPin, int actNb);
    void begin();
    void loadCalibration();
    void saveCalibration();
    void setTargetLength(float length);
    bool update(bool verbose = false);
    float getLength(bool verbose = false);
    int getRaw();
    void stop();
    void setSpeed(int speed);
    void setMin(int min);
    void setMax(int max);
    inline int getMin(){ return minPotValue; }
    inline int getMax(){ return maxPotValue; }
    int potPin;
private:
    CD74HC4067 pot_mux;
    MotorDriver driver;
    int minPotValue;
    int maxPotValue;
    int actuatorNb;
    float targetLength;
    float errorSum;
    float lastError;
    float length_data_buffer[ACT_LPF_N]; // Buffer for the last 10 readings
    int buffer_index = 0; // Index for the next reading to be added to the buffer
};

#endif // ACTUATOR_H