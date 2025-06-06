#include <Arduino.h>
#include <CD74HC4067.h>

CD74HC4067 lc_mux(16, 15, 14, 13); // S0, S1, S2, S3
#define LC_MUX_SIG_PIN 41 // Mux SIG pin
#define LC_MUX_EN_PIN 17 // Mux EN pin

CD74HC4067 pot_mux(22, 21, 20, 19); // S0, S1, S2, S3
#define POT_MUX_SIG_PIN 18 // Mux SIG pin for potentiometers
#define POT_MUX_EN_PIN 23 // Mux EN pin for potentiometers

void setup() {
    Serial.begin(9600);
    pinMode(LC_MUX_SIG_PIN, INPUT); // Mux SIG pin
    pinMode(LC_MUX_EN_PIN, OUTPUT); // Mux EN pin
    digitalWrite(LC_MUX_EN_PIN, LOW); // Enable the Mux
    Serial.println("LC Mux setup complete");

    // Initialize the potentiometer mux
    pinMode(POT_MUX_SIG_PIN, INPUT); // Mux SIG pin for potentiometers
    pinMode(POT_MUX_EN_PIN, OUTPUT); // Mux EN pin for potentiometers
    digitalWrite(POT_MUX_EN_PIN, LOW); // Enable the potentiometer Mux
}

void loop() {
    lc_mux.channel(13); // Select channel 13 for load cell
    int lc_value = analogRead(LC_MUX_SIG_PIN);
    Serial.print("Load Cell Value: ");
    Serial.println(lc_value);

    pot_mux.channel(0); // Select channel 0 for potentiometer
    int pot_value = analogRead(POT_MUX_SIG_PIN);
    Serial.print("Potentiometer Value: ");
    Serial.println(pot_value);

    // Read all channels of the load cell mux
    for (int i = 7; i < 16; i++) {
        lc_mux.channel(i);
        int value = analogRead(LC_MUX_SIG_PIN);
        Serial.print(" LC ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(value);
    }

    Serial.println();

    // Read all channels of the potentiometer mux
    for (int i = 0; i < 6; i++) {
        pot_mux.channel(i);
        int value = analogRead(POT_MUX_SIG_PIN);
        Serial.print(" Pot ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(value);
    }

    Serial.println();
    
    delay(1000); // Wait for a second before the next reading
}