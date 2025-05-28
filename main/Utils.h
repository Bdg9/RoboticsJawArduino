#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include <SD.h>
#include <SPI.h>

inline float mapFloat(int x, int in_min, int in_max, float out_min, float out_max) {
  return ((float)(x - in_min)) * (out_max - out_min) / (float)(in_max - in_min) + out_min;
}

inline float degrees2rad(float deg){
  return deg * DEG_TO_RAD; 
}

inline float rad2degrees(float rad){
  return rad * RAD_TO_DEG;
}

inline void listCSVFiles() {
  String fileNames[20];
  int fileCount = 0;

  File root = SD.open("robotics_jaw/");
  //if directory does not exist, print error and return
  if (!root) {
    Serial.println("Failed to open directory.");
    return;
  }
  if (!root.isDirectory()) {
    Serial.println("Not a directory.");
    return;
  }
  Serial.println("Listing CSV files:");
  fileCount = 0;

  while (true) {
    File entry = root.openNextFile();
    if (!entry) break;

    if (!entry.isDirectory() && String(entry.name()).endsWith(".csv")) {
      if (fileCount < 20) {
        fileNames[fileCount] = entry.name();
        fileCount++;
      }
    }
    entry.close();
  }

  //send the file names in a single line
  for (int i = 0; i < fileCount; i++) {
      Serial.print(fileNames[i]);
      if (i < fileCount - 1) {
      Serial.print(", ");
      }
  }
  Serial.println();
}

#endif
  