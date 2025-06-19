#ifndef PINLAYOUT_H
#define PINLAYOUT_H

//Actuator 1
#define MOTOR_1_PWM_PIN 33
#define MOTOR_1_A_PIN 34
#define MOTOR_1_B_PIN 36
#define MOTOR_1_POT_PIN 23

//Actuator 2
#define MOTOR_2_PWM_PIN 8
#define MOTOR_2_A_PIN 12
#define MOTOR_2_B_PIN 6
#define MOTOR_2_POT_PIN 21

//Actuator 3
#define MOTOR_3_PWM_PIN 5
#define MOTOR_3_A_PIN 4
#define MOTOR_3_B_PIN 3
#define MOTOR_3_POT_PIN 20

//Actuator 4
#define MOTOR_4_PWM_PIN 2
#define MOTOR_4_A_PIN 1
#define MOTOR_4_B_PIN 0
#define MOTOR_4_POT_PIN 17

//Actuator 5
#define MOTOR_5_PWM_PIN 29
#define MOTOR_5_A_PIN 28
#define MOTOR_5_B_PIN 27
#define MOTOR_5_POT_PIN 16

// Actuator 6
#define MOTOR_6_PWM_PIN 25
#define MOTOR_6_A_PIN 26
#define MOTOR_6_B_PIN 24
#define MOTOR_6_POT_PIN 15

// vector of pwm pin
const int PWM_PINS[6] = {33, 8, 5, 2, 29, 25};
// vector of A pin
const int A_PINS[6] = {34, 12, 4, 1, 28, 26};
// vector of B pin
const int B_PINS[6] = {36, 6, 3, 0, 27, 24};
// vector of pot pin
const int POT_PINS[6] = {23, 21, 20, 17, 16, 15};

#endif // PINLAYOUT_H