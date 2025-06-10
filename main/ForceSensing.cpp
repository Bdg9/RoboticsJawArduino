#include "ForceSensing.h"

ForceSensing::ForceSensing(): lc_mux(LC_MUX_S0, LC_MUX_S1, LC_MUX_S2, LC_MUX_S3),
                             lc_front(lc_mux, LC_FRONT[0], LC_FRONT[1], LC_FRONT[2]),
                             lc_back_r(lc_mux, LC_BACK_R[0], LC_BACK_R[1], LC_BACK_R[2]),
                             lc_back_l(lc_mux, LC_BACK_L[0], LC_BACK_L[1], LC_BACK_L[2]) {
    pinMode(LC_MUX_SIG, INPUT); // Mux SIG pin
    pinMode(LC_MUX_EN, OUTPUT); // Mux EN pin
    digitalWrite(LC_MUX_EN, LOW); // Enable the Mux

    // Put mux on the front load cell channel
    lc_mux.channel(LC_FRONT[2]); // Select channel for front load cell
}

void ForceSensing::update() {
    lc_front.update();
    lc_back_r.update();
    lc_back_l.update();

    // Read the force vectors from each load cell
    ForceVector frontForce = lc_front.readForce();
    ForceVector backRForce = lc_back_r.readForce();
    ForceVector backLForce = lc_back_l.readForce();

    // Combine the forces into a single force vector TODO see if we need to apply any scaling or calibration
    force.x = frontForce.x + backLForce.x;
    force.y = frontForce.y + backLForce.y;
    force.z = frontForce.z + backRForce.z + backLForce.z;
}

ForceVector ForceSensing::getTotalForce() const {
    return force;
}

void ForceSensing::printForce() const {
    ForceVector totalForce = getTotalForce();
    unsigned long currentTime = millis();
    Serial.print("Total Force - X: ");
    Serial.print(totalForce.x);
    Serial.print(", Y: ");
    Serial.print(totalForce.y);
    Serial.print(", Z: ");
    Serial.print(totalForce.z);
    Serial.print(", Time: ");
    Serial.println(currentTime);
    
    Serial.print("Front Force - X: ");
    Serial.print(lc_front.getForce().x);
    Serial.print(", Y: ");
    Serial.print(lc_front.getForce().y);
    Serial.print(", Z: ");
    Serial.print(lc_front.getForce().z);
    Serial.print(", Time: ");
    Serial.println(currentTime);
    
    Serial.print("Back Right Force - X: ");
    Serial.print(lc_back_r.getForce().x);
    Serial.print(", Y: ");
    Serial.print(lc_back_r.getForce().y);
    Serial.print(", Z: ");
    Serial.print(lc_back_r.getForce().z);
    Serial.print(", Time: ");
    Serial.println(currentTime);
    
    Serial.print("Back Left Force - X: ");
    Serial.print(lc_back_l.getForce().x);
    Serial.print(", Y: ");
    Serial.print(lc_back_l.getForce().y);
    Serial.print(", Z: ");
    Serial.print(lc_back_l.getForce().z);
    Serial.print(", Time: ");
    Serial.println(currentTime);
}

void ForceSensing::tareAll() {
    lc_front.tare();
    lc_back_r.tare();
    lc_back_l.tare();
}

