#include <Arduino.h>
#include <CD74HC4067.h>
#include "Config.h"
#include "Actuator.h"

int speed = 100; // Speed for the actuators
int loopTime = 5000; // Time to run each loop in milliseconds
CD74HC4067 pot_mux(POT_MUX_S0, POT_MUX_S1, POT_MUX_S2, POT_MUX_S3);
Actuator* actuators[6];
float targetLengths[6];

void setup() {
    Serial.begin(115200);
    while (!Serial) {
        ; // Wait for serial port to connect. Needed for native USB port only
    }
    pinMode(POT_MUX_SIG, INPUT); // Mux SIG pin for potentiometers
    pinMode(POT_MUX_EN, OUTPUT); // Mux EN pin for potentiometers
    digitalWrite(POT_MUX_EN, LOW); // Enable the potentiometer Mux
        
    // Initialize actuators
    for (int i = 0; i < 6; i++) {
        actuators[i] = new Actuator(pot_mux, ACT_PWM_PINS[i], ACT_A_PINS[i], ACT_B_PINS[i], ACT_POT_CH[i], i);
        actuators[i]->begin();
    }
    delay(2000); // Wait for actuators to initialize
    
    Serial.println("Actuators initialized.");
}

void loop() {
    unsigned long startTime = millis();
    for(int i = 0; i < 6; i++) {
        actuators[i]->setSpeed(speed);
    }
    while (millis() - startTime < loopTime) { // Run for 2 seconds
        //timestamp
        Serial.print(millis());
        for (int i = 0; i < 6; i++) {
            int raw = actuators[i]->getRaw(); // Get raw potentiometer value
            Serial.print(" Actuator ");
            Serial.print(i);
            Serial.print(": Length = ");
            Serial.print(raw);
        }
        Serial.println();
        delay(100); // Update every 200 ms
    }

    startTime = millis();
    for(int i = 0; i < 6; i++) {
        actuators[i]->setSpeed(-speed);
    }
    while (millis() - startTime < loopTime) { // Run for 2 seconds
        Serial.print(millis());
        for (int i = 0; i < 6; i++) {
            int raw = actuators[i]->getRaw(); // Get raw potentiometer value
            Serial.print(" Actuator ");
            Serial.print(i);
            Serial.print(": Length = ");
            Serial.print(raw);
        }
        Serial.println();
        delay(100); // Update every 200 ms
    }

    for(int i = 0; i < 6; i++) {
        actuators[i]->stop(); // Stop all actuators
    }
    Serial.println("All actuators stopped.");

    delay(5000); // Wait for 5 seconds before next iteration
    while(true){}
    
}

