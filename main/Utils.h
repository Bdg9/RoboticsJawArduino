#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>

inline float mapFloat(int x, int in_min, int in_max, float out_min, float out_max) {
  return ((float)(x - in_min)) * (out_max - out_min) / (float)(in_max - in_min) + out_min;
}

inline float degrees2rad(float deg){
  return deg * DEG_TO_RAD; 
}

inline float rad2degrees(float rad){
  return rad * RAD_TO_DEG;
}

#endif
  