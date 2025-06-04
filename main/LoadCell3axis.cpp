#include "LoadCell3axis.h"

LoadCell3Axis::LoadCell3Axis(Mux &mux, int muxPinX, int muxPinY, int muxPinZ)
    : _mux(mux), _chX(muxPinX), _chY(muxPinY), _chZ(muxPinZ) {
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
    int rawX = _mux.read(_chX);
    int rawY = _mux.read(_chY);
    int rawZ = _mux.read(_chZ);

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