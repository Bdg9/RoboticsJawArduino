#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

class MotorDriver {
public:
    MotorDriver(int pwmPin, int dirPin);
    void begin();
    void setSpeed(float speed); // speed in [-255,255]
private:
    int pwmPin, dirPin;
};

#endif // MOTOR_DRIVER_H