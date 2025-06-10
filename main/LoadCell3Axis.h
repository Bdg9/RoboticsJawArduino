#ifndef LOAD_CELL_3_AXIS_H
#define LOAD_CELL_3_AXIS_H
#include <Arduino.h>
#include <CD74HC4067.h>
#include "Config.h"

#define TARE_DELAY 500 // Delay for tare operation in milliseconds
//--------------------------------------------------------------------
// Simple vector container for a 3‑axis force reading (raw ADC counts
// or physical units if you apply scaling in user code).
//--------------------------------------------------------------------
struct ForceVector {
  float x;
  float y;
  float z;
};

class LoadCell3Axis {
public:
    LoadCell3Axis(CD74HC4067& lc_mux, int muxPinX, int muxPinY, int muxPinZ);
    
    // Initialize the load cell
    void update();
    
    // Read the force vector from the load cell
    ForceVector readForce();
    
    // Get the force vector
    ForceVector getForce() const;

    // Get raw data from the load cell for debug
    inline uint8_t getXRawData() const { return _xDataBuffer[_bufferIndex]; }
    inline uint8_t getYRawData() const { return _yDataBuffer[_bufferIndex]; }
    inline uint8_t getZRawData() const { return _zDataBuffer[_bufferIndex]; }

    // Tare the load cell
    void tare();

private:
  CD74HC4067 lc_mux; // Multiplexer for load cell
  uint8_t  _chX, _chY, _chZ;
  uint8_t  _xDataBuffer[LC_SAMPLES] = {0};
  uint8_t  _yDataBuffer[LC_SAMPLES] = {0};
  uint8_t  _zDataBuffer[LC_SAMPLES] = {0};
  uint8_t  _bufferIndex = 0;
  ForceVector _force{0, 0, 0};
  ForceVector _forceTare{0, 0, 0}; // Tare values for each axis
  
};

#endif // LOAD_CELL_3_AXIS_H