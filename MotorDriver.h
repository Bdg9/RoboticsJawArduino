#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

class MotorDriver {
public:
    MotorDriver(int pwmPin, int in1Pin, int in2Pin);
    void begin();
    void setSpeed(float speed); // speed in [-255,255]
private:
    int pwmPin, in1Pin, in2Pin;
};

#endif // MOTOR_DRIVER_H