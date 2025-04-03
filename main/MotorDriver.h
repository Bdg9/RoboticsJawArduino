#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

class MotorDriver {
public:
    MotorDriver(int pwmPin, int aPin, int bPin);
    void begin();
    void setSpeed(float speed); // speed in [-255,255]
    void stop();
private:
    int pwmPin, aPin, bPin;
};

#endif // MOTOR_DRIVER_H