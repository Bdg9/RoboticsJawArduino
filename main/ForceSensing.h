#ifndef FORCE_SENSING_H
#define FORCE_SENSING_H

#include "LoadCell3Axis.h"
#include "Config.h"
#include <CD74HC4067.h>

class ForceSensing {
public:
    ForceSensing();
    
    // Update the force readings
    bool update();
    
    // Get the current force vector
    ForceVector getTotalForce() const;
    
    // Get the force vector from each load cell
    ForceVector getFrontForce() const { return lc_front.getForce(); }
    ForceVector getBackRightForce() const { return lc_back_r.getForce(); }
    ForceVector getBackLeftForce() const { return lc_back_l.getForce(); }

    // Print the current force vector to Serial
    void printForce() const;

    // Tare the force vectors of all load cells
    void tareAll();

private:
    CD74HC4067 lc_mux; // Multiplexer for load cells
    LoadCell3Axis lc_front; // Front load cell
    LoadCell3Axis lc_back_r; // Back right load cell
    LoadCell3Axis lc_back_l; // Back left load cell
    ForceVector force; // Current force vector
};

#endif // FORCE_SENSING_H