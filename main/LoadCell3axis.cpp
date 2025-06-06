#include "LoadCell3axis.h"

LoadCell3Axis::LoadCell3Axis(CD74HC4067& lc_mux, int muxPinX, int muxPinY, int muxPinZ)
    : lc_mux(lc_mux), _chX(muxPinX), _chY(muxPinY), _chZ(muxPinZ) {
}

void LoadCell3Axis::update() {
    // Read the force vector from the load cell
    ForceVector force = readForce();
    
    // Update the internal force vector
    _force.x = force.x;
    _force.y = force.y;
    _force.z = force.z;
}

ForceVector LoadCell3Axis::getForce() const {
    return _force;
}

//use circular buffer to read the force vector
ForceVector LoadCell3Axis::readForce() {
    lc_mux.channel(_chX); // Select channel for X
    int rawX = analogRead(LC_MUX_SIG); // Read the raw value from the mux
    lc_mux.channel(_chY); // Select channel for Y
    int rawY = analogRead(LC_MUX_SIG); // Read the raw value from the mux
    lc_mux.channel(_chZ); // Select channel for Z
    int rawZ = analogRead(LC_MUX_SIG); // Read the raw value from the mux

    // add values to the circular buffer
    _xDataBuffer[_bufferIndex] = rawX;
    _yDataBuffer[_bufferIndex] = rawY;
    _zDataBuffer[_bufferIndex] = rawZ;
    _bufferIndex = (_bufferIndex + 1) % LC_SAMPLES;

    // Calculate the average force vector
    float avgX = 0, avgY = 0, avgZ = 0;
    for (int i = 0; i < LC_SAMPLES; i++) {
        avgX += _xDataBuffer[i];
        avgY += _yDataBuffer[i];
        avgZ += _zDataBuffer[i];
    }

    avgX /= LC_SAMPLES;
    avgY /= LC_SAMPLES;
    avgZ /= LC_SAMPLES;

    // Convert raw values to force vector (you may need to apply calibration/scaling)
    ForceVector force;
    force.x = map(avgX, LOAD_CELL_MIN, LOAD_CELL_MAX, LOAD_CELL_MIN_FORCE, LOAD_CELL_MAX_FORCE);
    force.y = map(avgY, LOAD_CELL_MIN, LOAD_CELL_MAX, LOAD_CELL_MIN_FORCE, LOAD_CELL_MAX_FORCE);
    force.z = map(avgZ, LOAD_CELL_MIN, LOAD_CELL_MAX, LOAD_CELL_MIN_FORCE, LOAD_CELL_MAX_FORCE);

    // Clamp the force values to prevent overflow
    force.x = constrain(force.x, LOAD_CELL_MIN_FORCE, LOAD_CELL_MAX_FORCE);
    force.y = constrain(force.y, LOAD_CELL_MIN_FORCE, LOAD_CELL_MAX_FORCE);
    force.z = constrain(force.z, LOAD_CELL_MIN_FORCE, LOAD_CELL_MAX_FORCE);
    return force;
}