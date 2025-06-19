#include <Arduino.h>

void setup() {
    Serial.begin(9600);

    // Initialize all teensy 4.1 analog pins to input mode
    for(int i=14 ; i <= 27; i++ ) {
        pinMode(i, INPUT);
    }

    for(int i=38 ; i <= 41; i++ ) {
        pinMode(i, INPUT);
    }
}

void loop() {
    // Read all analog pins and print their values
    for(int i=14 ; i <= 27; i++ ) {
        int value = analogRead(i);
        Serial.print(" Pin ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(value);
    }

    for(int i=38 ; i <= 41; i++ ) {
        int value = analogRead(i);
        Serial.print(" Pin ");
        Serial.print(i);
        Serial.print(": ");
        Serial.println(value);
    }

    delay(1000); // Wait for a second before the next reading
}