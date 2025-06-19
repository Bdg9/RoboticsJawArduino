#include <Arduino.h>

#define C_Z_PIN 38
#define C_Y_PIN 22
#define C_X_PIN 20
#define BUILTIN_LED 13

void setup() {
    Serial.begin(9600);
    pinMode(C_Z_PIN, INPUT);
    pinMode(C_Y_PIN, INPUT);
    pinMode(C_X_PIN, INPUT);
    pinMode(BUILTIN_LED, OUTPUT);
    Serial.print("init done");
}

void loop() {
    // Read the load cell value
    int Z_loadCellValue = analogRead(C_Z_PIN);
    int Y_loadCellValue = analogRead(C_Y_PIN);
    int loadCellValue = analogRead(C_X_PIN);
    
    // Print the value to the Serial Monitor
    Serial.print("Load Cell Value, X: ");
    Serial.print(loadCellValue);
    Serial.print(", Y: ");
    Serial.print(Y_loadCellValue);
    Serial.print(", Z: ");
    Serial.println(Z_loadCellValue);

    // blink led
    digitalWrite(BUILTIN_LED, HIGH);  // Turn the LED on
    delay(200);                       // Wait for 100 milliseconds  
    digitalWrite(BUILTIN_LED, LOW);   // Turn the LED off
    delay(200);                       // Wait for 400 milliseconds
    
}